/* Citizen Module - Shared JavaScript */


/* ===== Forgot Password ===== */
async function sendOTP(){

let email=document.getElementById("email").value.trim();

if(email===""){
alert("Please enter your email.");
return;
}

document.getElementById("loader").style.display="block";
document.getElementById("otpBtn").disabled=true;

try{

const response=await fetch("/send-otp",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
email:email
})

});

const data=await response.json().catch(()=>({success:false,message:"The server returned an invalid response."}));

document.getElementById("loader").style.display="none";
document.getElementById("otpBtn").disabled=false;

if(data.success){

// Store email for resend OTP
sessionStorage.setItem("resetEmail", email);

document.getElementById("message").style.display="block";
document.getElementById("message").innerHTML="OTP sent successfully. Redirecting...";

setTimeout(function(){

window.location.href="/verify-otp";

},1200);

}
else{

alert(data.message || "Unable to send the OTP.");

}

}
catch(error){

document.getElementById("loader").style.display="none";
document.getElementById("otpBtn").disabled=false;

alert("Unable to connect to the server.");

}

}

/* ===== Login ===== */
function loginTogglePassword(){

const input=document.getElementById("password");
const icon=document.querySelector(".toggle");

if(input.type==="password"){

input.type="text";
icon.innerHTML="🙈";

}else{

input.type="password";
icon.innerHTML="👁";

}

}

async function login(){

const username=document.getElementById("username").value.trim();
const password=document.getElementById("password").value;

const message=document.getElementById("message");
const errorMessage=document.getElementById("errorMessage");

message.style.display="none";
errorMessage.style.display="none";

if(!username || !password){

errorMessage.innerHTML="Please enter username and password.";
errorMessage.style.display="block";
return;

}

document.getElementById("loader").style.display="block";
document.getElementById("loginBtn").disabled=true;

try{

const response=await fetch("/login",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
username:username,
password:password
})

});

const data=await response.json().catch(()=>({success:false,message:"The server returned an invalid response."}));

document.getElementById("loader").style.display="none";
document.getElementById("loginBtn").disabled=false;

if(data.success){

message.innerHTML="Login successful! Redirecting...";
message.style.display="block";

setTimeout(function(){

window.location.href="/";

},1000);

}
else{

errorMessage.innerHTML=data.message || "Login failed. Please try again.";
errorMessage.style.display="block";

}

}
catch(error){

document.getElementById("loader").style.display="none";
document.getElementById("loginBtn").disabled=false;

errorMessage.innerHTML="Unable to connect to the server. Check that Flask is running on port 5000.";
errorMessage.style.display="block";

}

}

/* ===== Register ===== */
function registerTogglePassword(id,icon){

const input=document.getElementById(id);

if(input.type==="password"){

input.type="text";
icon.innerHTML="🙈";

}else{

input.type="password";
icon.innerHTML="👁";

}

}

function registerCheckStrength(){

const password=document.getElementById("password").value;

const strength=document.getElementById("strength");

if(password.length<6){

strength.innerHTML="🔴 Weak Password";
strength.style.color="red";

}
else if(password.length<10){

strength.innerHTML="🟡 Medium Password";
strength.style.color="orange";

}
else{

strength.innerHTML="🟢 Strong Password";
strength.style.color="green";

}

}

async function register(){

const fullName=document.getElementById("fullName").value.trim();
const mobile=document.getElementById("mobile").value.trim();
const houseNumber=document.getElementById("houseNumber").value.trim();
const wardNumber=document.getElementById("wardNumber").value;
const gender=document.getElementById("gender").value;
const email=document.getElementById("email").value.trim();
const address=document.getElementById("address").value.trim();
const username=document.getElementById("username").value.trim();
const password=document.getElementById("password").value;
const confirmPassword=document.getElementById("confirmPassword").value;

const message=document.getElementById("message");
const errorMessage=document.getElementById("errorMessage");

message.style.display="none";
errorMessage.style.display="none";

if(!fullName || !mobile || !houseNumber || !wardNumber || !gender || !email || !address || !username || !password || !confirmPassword){

errorMessage.innerHTML="Please fill all fields.";
errorMessage.style.display="block";
return;

}

if(mobile.length!==10 || !/^\d{10}$/.test(mobile)){

errorMessage.innerHTML="Please enter a valid 10-digit mobile number.";
errorMessage.style.display="block";
return;

}

if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){

errorMessage.innerHTML="Please enter a valid email address.";
errorMessage.style.display="block";
return;

}

if(password!==confirmPassword){

errorMessage.innerHTML="Passwords do not match.";
errorMessage.style.display="block";
return;

}

if(password.length<6){

errorMessage.innerHTML="Password must be at least 6 characters.";
errorMessage.style.display="block";
return;

}

document.getElementById("loader").style.display="block";
document.getElementById("registerBtn").disabled=true;

try{

const response=await fetch("/register",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
full_name:fullName,
mobile_number:mobile,
house_number:houseNumber,
ward_number:wardNumber,
gender:gender,
email:email,
address:address,
username:username,
password:password
})

});

const data=await response.json().catch(()=>({success:false,message:"The server returned an invalid response."}));

document.getElementById("loader").style.display="none";
document.getElementById("registerBtn").disabled=false;

if(data.success){

message.innerHTML="Registration successful! Redirecting to login...";
message.style.display="block";

setTimeout(function(){

window.location.href="/login";

},1500);

}
else{

errorMessage.innerHTML=data.message || "Registration failed. Please try again.";
errorMessage.style.display="block";

}

}
catch(error){

document.getElementById("loader").style.display="none";
document.getElementById("registerBtn").disabled=false;

errorMessage.innerHTML="Unable to connect to the server.";
errorMessage.style.display="block";

}

}

/* ===== Reset Password ===== */
function resetTogglePassword(id,icon){

const input=document.getElementById(id);

if(input.type==="password"){

input.type="text";
icon.innerHTML="🙈";

}else{

input.type="password";
icon.innerHTML="👁";

}

}

function resetCheckStrength(){

const password=document.getElementById("password").value;

const strength=document.getElementById("strength");

if(password.length<6){

strength.innerHTML="🔴 Weak Password";
strength.style.color="red";

}
else if(password.length<10){

strength.innerHTML="🟡 Medium Password";
strength.style.color="orange";

}
else{

strength.innerHTML="🟢 Strong Password";
strength.style.color="green";

}

}

async function updatePassword(){

const password=document.getElementById("password").value;
const confirm=document.getElementById("confirmPassword").value;

if(password==="" || confirm===""){

alert("Please fill all fields.");

return;

}

if(password!==confirm){

alert("Passwords do not match.");

return;

}

if(password.length<6){

alert("Password must be at least 6 characters.");

return;

}

try{

const response=await fetch("/update-password",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
password:password
})

});

const data=await response.json().catch(()=>({success:false,message:"The server returned an invalid response."}));

if(data.success){

alert("Password updated successfully!");

window.location.href="/login";

}else{

alert(data.message || "Password update failed.");

}

}
catch{

alert("Server error.");

}

}
/* ===== Verify OTP ===== */
const otpInputs=document.querySelectorAll(".otp");

document.addEventListener("DOMContentLoaded", function(){

if(!otpInputs.length){
    return;
}

// Auto move to next box
otpInputs.forEach((input,index)=>{

input.addEventListener("input",()=>{

if(input.value.length===1 && index<otpInputs.length-1){

otpInputs[index+1].focus();

}

});

input.addEventListener("keydown",(e)=>{

if(e.key==="Backspace" && input.value==="" && index>0){

otpInputs[index-1].focus();

}

});

});

// Countdown Timer
let seconds=60;

const timer=setInterval(()=>{

seconds--;

document.getElementById("time").innerText=seconds;

if(seconds<=0){

clearInterval(timer);

document.getElementById("resendBtn").disabled=false;

}

},1000);

});

async function verifyOTP(){

let otp="";

otpInputs.forEach(input=>{

otp+=input.value;

});

if(otp.length!==6){

alert("Please enter the complete OTP.");

return;

}

try{

const response=await fetch("/verify-otp",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
otp:otp
})

});

const data=await response.json().catch(()=>({success:false,message:"The server returned an invalid response."}));

if(data.success){

window.location.href="/reset-password";

}
else{

alert(data.message || "OTP verification failed.");

}

}
catch{

alert("Server error.");

}

}

// Countdown Timer removed from original; initialized above.

async function resendOTP(){

try{

const response=await fetch("/send-otp",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
email:sessionStorage.getItem("resetEmail") || ""
})

});

const data=await response.json();

if(data.success){

alert("OTP Sent Again.");

location.reload();

}

}
catch{

alert("Unable to resend OTP.");

}

}
