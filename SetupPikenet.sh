#!/bin/bash
echo "This product requires python 3 to be pre-installed in the environment"
yes | sudo apt install python3-venv > /dev/null 2>&1

# Optional: create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    sudo python3 -m venv venv
fi


# Activate virtual environment
echo "Enabling virtual environment..."
source ./venv/bin/activate

# Upgrade pip
echo "Ensuring pip status..."
yes | sudo apt install python3-pip > /dev/null 2>&1
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
if [ -f requirements.txt ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

# Optional: check for environment variables
echo "Searching for environment variables..."
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "$SECRET_KEY" ]; then
    echo "Warning: FLASK_SECRET_KEY not set. Using default (not secure for production)."
    export SECRET_KEY="dev"
fi
APPNAME="PikeNet"
if [ ! -d "postgresql-16.2" ]; then

echo "Preparing postgres..."
mkdir -p $HOME/$APPNAME/pgsql
if [ ! -f postgresql-16.2.tar.gz ]; then
echo "Downloading postgres..."
sudo curl -O https://ftp.postgresql.org/pub/source/v16.2/postgresql-16.2.tar.gz
else
echo "Postgresq already downloaded"
fi
sudo tar -xf postgresql-16.2.tar.gz

# Readline is required for any psql interaction ( terminal database editing )
yes | sudo apt install libreadline-dev
echo "Configuring postgres..."
cd postgresql-16.2
./configure --without-icu -prefix=$HOME/$APPNAME/pgsql > /dev/null 2>&1 # No icu makes it hard for postgres to handle foreign characters, ensure english is the only required language
echo "Building postgres..."
make -j$(nproc) > /dev/null 2>&1

make install > /dev/null 2>&1
cd ..
else
echo "Postgres already installed"
fi

if [ ! -d "~/$APPNAME/local/data" ]; then
	echo "Initializing first database..."
	~/$APPNAME/pgsql/bin/initdb -D ~/$APPNAME/local/data
	~/$APPNAME/pgsql/bin/pg_ctl -D ~/$APPNAME/local/data -l ~/$APPNAME/logfile start -o "-p 5433"
	
	~/$APPNAME/pgsql/bin/createuser -p 5433 pikenet-database-owner
	~/$APPNAME/pgsql/bin/createdb -p 5433 pikenet-database -O pikenet-database-owner

	#IDK IF THIS WORKS
	~/$APPNAME/pgsql/bin/psql -p 5433 -d pikenet-database -c "ALTER USER \"pikenet-database-owner\" WITH PASSWORD 'your_password_here';"

	echo "Creating 'users' table..."
~/$APPNAME/pgsql/bin/psql -h localhost -p 5433 -U pikenet-database-owner -d pikenet-database <<EOF
-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    password VARCHAR(200) NOT NULL,
    auth_value INTEGER NOT NULL DEFAULT 2
);

-- Create default admin
INSERT INTO users (username, email, password, auth_value)
VALUES ('pikemin', NULL, 'pikemin', 0)
ON CONFLICT (username) DO NOTHING;

-- Create the notes table
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create the tags table
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Create the join table to link notes and tags
CREATE TABLE IF NOT EXISTS note_tags (
    note_id INT NOT NULL,
    tag_id INT NOT NULL,
    
    PRIMARY KEY (note_id, tag_id),
    
    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

EOF

EOF
else
	echo "Database already created, skipping step..."
fi

# Create new dynamic folder for server to write to
mkdir -p dynamic

# Change ownership to the Apache user and group
chown -R www-data:www-data dynamic

# Give read/write/execute permissions to owner and group
chmod -R 775 dynamic

# Add sticky bit so child folders inherit permissions
chmod g+s dynamic

# Now enter the new dynamic folder and make subfolders
cd dynamic
mkdir -p snack_images


# Exit back to root directory
cd ..

# Run Flask app
echo "Starting web application..."
python3 ThePikeNet.py
