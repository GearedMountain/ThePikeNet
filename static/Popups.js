  //Popup message handler
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
      
        errorPopup.classList.add('bg-red-500', 'text-white', 'p-4', 'rounded-md', 'shadow-md', 'max-w-sm', 'absolute', 'bottom-6', 'right-6', 'fade-in-popup');
        closeButton.classList.add('absolute', 'top-2', 'right-2', 'text-white', 'text-xl');

      } else if (status === 1){

        errorPopup.classList.add('bg-green-500', 'text-white', 'p-4', 'rounded-md', 'shadow-md', 'max-w-sm', 'absolute', 'bottom-6', 'right-6', 'fade-in-popup');
        closeButton.classList.add('absolute', 'top-2', 'right-2', 'text-white', 'text-xl');

      } else if (status === 2){

        errorPopup.classList.add('bg-gray-500', 'text-white', 'p-4', 'rounded-md', 'shadow-md', 'max-w-sm', 'absolute', 'bottom-6', 'right-6', 'fade-in-popup');
        closeButton.classList.add('absolute', 'top-2', 'right-2', 'text-white', 'text-xl');

      } else{

        errorPopup.classList.add('bg-yellow-500', 'text-white', 'p-4', 'rounded-md', 'shadow-md', 'max-w-sm', 'absolute', 'bottom-6', 'right-6', 'fade-in-popup');
        closeButton.classList.add('absolute', 'top-2', 'right-2', 'text-white', 'text-xl');

      }
        closeButton.innerHTML = '&times;'; // Close icon

      // Add an event listener to the close button to hide the popup
      closeButton.addEventListener('click', () => {
        errorPopup.remove();
      });
    // Add the close button to the error popup
      errorPopup.appendChild(closeButton);

      // Create the error message text
      const errorMessage = document.createElement('strong');
      errorMessage.textContent = header + '! ' + message;

      // Append the error message text to the error popup
      errorPopup.appendChild(errorMessage);

      // Append the error popup to the body of the document
      errorPopup.classList.add('fade-in-bottom-quick');
      document.body.appendChild(errorPopup);
      
      if(decay){
        setTimeout(() => {
          errorPopup.classList.add('fade-out-popup');
          setTimeout(() => { errorPopup.remove();}, 2000);
        }, 6000);
        }
}

function attentionElement(status, name, decayType) {

    const element = document.getElementById(name);

    var newClass = ""
    if (status === 0){
        newClass = "border-red-500";
    } else{
        newClass = "border-yellow-500";
    }

    element.classList.add("transition-colors") 
    element.classList.add("duration-200")     
    element.classList.add(newClass)   
    
    // decay has 3 types:
    // 0 = none
    // 1 = flicker ( 300 ms )
    // 2 = long ( 4000 ms )
    
    
    
    if(decayType === "Flicker"){
        setTimeout(() => {
          element.classList.remove(newClass)
        }, 300);}
        
    // Basically a double flicker
    if(decayType === "Pulse"){
        setTimeout(() => { 
          element.classList.remove(newClass)
          setTimeout(() => {
            element.classList.add(newClass)
            setTimeout(() => {
                element.classList.remove(newClass)
            }, 300);
            }, 300);
        }, 300);}
    if(decayType === "Long"){
        setTimeout(() => {
          element.classList.remove(newClass)
        }, 4000);
    }
}

// Helper function to sleep
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
