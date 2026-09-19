function togglePassword(){

    const input = document.getElementById("password");
    const icon = document.querySelector(".toggle");

    if(input.type === "password"){

        input.type = "text";
        icon.innerHTML = "🙈";

    }else{

        input.type = "password";
        icon.innerHTML = "👁";

    }

}


async function login(){

    const username =
        document.getElementById("username").value.trim();

    const password =
        document.getElementById("password").value;

    const message =
        document.getElementById("message");

    const errorMessage =
        document.getElementById("errorMessage");


    message.style.display = "none";
    errorMessage.style.display = "none";


    if(!username || !password){

        errorMessage.innerHTML =
            "Please enter username and password.";

        errorMessage.style.display = "block";

        return;
    }


    document.getElementById("loader").style.display = "block";

    document.getElementById("loginBtn").disabled = true;


    try{

        const response = await fetch("/login",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                username:username,
                password:password

            })

        });


        const data = await response.json().catch(() => ({

            success:false,

            message:
                "The server returned an invalid response."

        }));


        document.getElementById("loader").style.display = "none";

        document.getElementById("loginBtn").disabled = false;


        if(data.success){

            message.innerHTML =
                "Login successful! Redirecting...";

            message.style.display = "block";


            setTimeout(function(){

                window.location.href = "/";

            },1000);


        }else{

            errorMessage.innerHTML =
                data.message ||
                "Login failed. Please try again.";

            errorMessage.style.display = "block";

        }


    }catch(error){

        document.getElementById("loader").style.display = "none";

        document.getElementById("loginBtn").disabled = false;


        errorMessage.innerHTML =
            "Unable to connect to the server. Check that Flask is running on port 5000.";

        errorMessage.style.display = "block";

    }

}
