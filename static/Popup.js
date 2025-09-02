function showPopup(status, message, decay) {
       // Status codes are as follows
       // 0 - Error ( red )
       // 1 - Success ( green )
       // 2 - Information ( white )
       // 3 - Warning ( yellow )

       const popupValues = ["Error","Success","Information","Warning"]
       var header = popupValues[status];
       // Create the the error popup
       const errorPopup = document.createElement('div');
       const closeButton = document.createElement('button');
       if(status === 0){

         errorPopup.classList.add('bg-red-500', 'text-white', 'p-4',
'rounded-md', 'shadow-md', 'max-w-sm', 'absolute', 'bottom-6',
'right-6', 'fade-in-popup');
         closeButton.classList.add('absolute', 'top-2', 'right-2',
'text-white', 'text-xl');

       } else if (status === 1){

         errorPopup.classList.add('bg-green-500', 'text-white', 'p-4',
'rounded-md', 'shadow-md', 'max-w-sm', 'absolute', 'bottom-6',
'right-6', 'fade-in-popup');
         closeButton.classList.add('absolute', 'top-2', 'right-2',
'text-white', 'text-xl');

       } else if (status === 2){

         errorPopup.classList.add('bg-gray-500', 'text-white', 'p-4',
'rounded-md', 'shadow-md', 'max-w-sm', 'absolute', 'bottom-6',
'right-6', 'fade-in-popup');
         closeButton.classList.add('absolute', 'top-2', 'right-2',
'text-white', 'text-xl');

       } else{

         errorPopup.classList.add('bg-yellow-500', 'text-white', 'p-4',
'rounded-md', 'shadow-md', 'max-w-sm', 'absolute', 'bottom-6',
'right-6', 'fade-in-popup');
         closeButton.classList.add('absolute', 'top-2', 'right-2',
'text-white', 'text-xl');

       }
         closeButton.innerHTML = '&times;'; // Close icon

       // Add an event listener to the close button to hide the popup
       closeButton.addEventListener('click', () => {
         errorPopup.style.display = 'none';
       });
     // Add the close button to the error popup
       errorPopup.appendChild(closeButton);

       // Create the error message text
       const errorMessage = document.createElement('strong');
       errorMessage.textContent = header + '! ' + message;

       // Append the error message text to the error popup
       errorPopup.appendChild(errorMessage);

       // Append the error popup to the body of the document
       document.body.appendChild(errorPopup);


       if(decay){
         setTimeout(() => {
           errorPopup.classList.add('fade-out-popup');
         }, 6000);}
       }