function validateCustomer(formData) {
    var x = document.forms["IDForm"]["customerName"].value;
    var regex = "^.{2,}[\-].{,5}"



    if (x == "") {
      alert("Customer name must be filled out");
      return false;
    }
    if(regex.test(x.value) == false) {
        alert("Customer name format incorrect.")
        return false;
    }
}