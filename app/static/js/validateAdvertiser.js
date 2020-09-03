function validateAdvertiser(formData) {
    var y = document.forms["IDForm"]["advertiserName"].value;
    var regex = "^.{2,}[\-].{,5}"

    if (y == "") {
        alert("Advertiser name must be filled out");
        return false;
    }
    if(regex.test(y.value) == false) {
        alert("Advertiser name format incorrect.")
        return false;
    }
}