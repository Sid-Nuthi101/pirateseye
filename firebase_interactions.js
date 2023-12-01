// https://firebase.google.com/docs/web/setup#available-libraries
console.log(aws_api)
// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyCPQJ9gXWoqtRQt1gt9XfCvJbSHitj9ZFc",
    authDomain: "pirate-s-eye.firebaseapp.com",
    projectId: "pirate-s-eye",
    storageBucket: "pirate-s-eye.appspot.com",
    messagingSenderId: "544998343545",
    appId: "1:544998343545:web:5daeeff324d05a5951e5a8",
    measurementId: "G-58ET6P48J3"
};


// Initialize Firebase
firebase.initializeApp(firebaseConfig);
var firestore = firebase.firestore();
const analytics = firebase.analytics();
var createdUser = false;
var global_user = null;
function signInWithGoogle() {
    const provider = new firebase.auth.GoogleAuthProvider();
    firebase.auth().signInWithPopup(provider)
        .then((result) => {
            // You can access the Google User in result.user
            console.log(`Hello ${result.user.displayName}!`);
            if (result.additionalUserInfo.isNewUser) {
                createdUser = true;
                console.log("This is a new user.");
            } else {
                console.log("This is an existing user.");
            }
        })
        .catch((error) => {
            console.error("Error signing in with Google", error);
        });
}

if(location.href.split("/").slice(-1)[0].split("?")[0]=="login.html"){
    $(".google-btn").click(signInWithGoogle);
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            // User is signed in.
            console.log(user);
            if(createdUser){
                firestore.collection("users").doc(user.uid).set({
                    "email":user.email,
                    "verifiedUser":false
                }).then(function(){
                    location.href="/articles/list-articles.html";
                });
            }else{
                location.href="/articles/list-articles.html";
            }
        } else {
            // No user is signed in.
            console.log("User is signed out");
        }
    });
}
else if(location.href.split("/").slice(-1)[0] == "manage-users.html" || location.href.split("/").slice(-1)[0] == "about.html"){
    if(location.href.split("/").slice(-1)[0] == "manage-users.html"){
        
        var usersRef = firestore.collection("users");

        usersRef.get().then(function(querySnapshot) { //Manage Users
            querySnapshot.forEach(function(doc) {
                const user = doc.data();
                const userEmail = user.email;
                // Display user's email
                const userDiv = document.createElement("div");
                console.log(user.email);
                console.log(global_user);
                if(user.email != global_user.email){
                    if(user.verifiedUser == false){
                        userDiv.innerHTML = `
                            <p>Email: ${userEmail}</p>
                            <button id="reject-${doc.id}" class="reject-button">Reject</button>
                            <button id="accept-${doc.id}" class="accept-button">Accept</button>
                        `;
                    } else{
                        userDiv.innerHTML = `
                            <p>Email: ${userEmail}</p>
                            <button id="reject-${doc.id}" class="reject-button">Remove</button>
                        `;
                    }
                    document.querySelector("#users-container").appendChild(userDiv);
                }
            });
            $(".reject-button").click(function(){ // Reject new user
                var id = $(this).attr("id");
                id = id.replace("reject-","");
                $(".confirm-menu h2").text("Are you sure you would like to remove "+$(this).parent().children("p").text().split(":")[1].trim()+" and no longer allow them to make changes to the Pirate's Eye?");
                displayConfirm(
                    function(){
                        $.ajax({
                            url:aws_api+"/verifyEmail",
                            method:"POST",
                            data:JSON.stringify({user:global_user.uid, edit_uid:id, edit_type:"remove"}),
                            success: function(res){
                                firestore.collection("users").doc(id).delete().then(() => {
                                    addNewAlert("success", "Successfully removed user");
                                    $("#reject-"+id).parent().remove();
                                }).catch(() => {
                                    addNewAlert("error", "Error removing user: " + res["body"]);
                                });
                            }
                        });
                    }
                );
            });
            $(".accept-button").click(function(){ // Accept new user
                var id = $(this).attr("id");
                id = id.replace("accept-","");
                $(".confirm-menu h2").text("Are you sure you would like to let "+$(this).parent().children("p").text().split(":")[1].trim()+" make changes to the Pirate's Eye?");
                displayConfirm(function(){
                    $.ajax({
                        url:aws_api+"/verifyEmail",
                        method:"POST",
                        data:JSON.stringify({user:global_user.uid, edit_uid:id, edit_type:"add"}),
                        success:function(res){
                            console.log(res);
                            if(res.statusCode == 200){
                                firestore.collection("users").doc(id).update({
                                    "verifiedUser":true,
                                }).then(() => {
                                    addNewAlert("success", "Successfully accepted user into organization.")
                                }).catch(() => {
                                    addNewAlert("error", "Error removing user");
                                });
                            } else{
                                addNewAlert("error", "Error accepting user");
                            }
                        },
                        error:function(res){
                            addNewAlert("danger","Error accepting user, please try again later.")
                        }
                    })
                });
            });
        });

        $(".edit-user-menu .year").append(`<option value="${new Date().getFullYear() - 1}">${new Date().getFullYear() - 1}</option>`);
        $(".edit-user-menu .year").append(`<option value="${new Date().getFullYear()}">${new Date().getFullYear()}</option>`);
    }

    function loadContributers(year_selected,year_obj){ // Load all the editors
        $("#contributers-container").html("");
        for(contributer of Object.keys(year_obj)){
            
            var contributer_id = contributer;
            contributer = year_obj[contributer];
            $("#contributers-container").append(`
                <div id="${contributer_id}">
                    <img src="/images/editors/${contributer.image}"/>
                    <h3>${contributer.name}</h3>
                    <p>${truncateString(contributer.description,100)}</p>
                    <div class="role-info">${contributer.title}</div>
                    <button class="edit-contributer">Edit</button>
                    <button class="remove-contributer">Remove</button>
                </div>
            `);
        }
        $(".remove-contributer").off("click").click(function(){
            var contributer_id = $(this).parent().attr("id");
            contributer = year_obj[contributer_id];
            $(".confirm-menu > h2").text("Are you sure you would like to remove "+contributer.name+"?");

            displayConfirm(function(){
                $.ajax({
                    url:aws_api+"/EditContributer",
                    method:"POST",
                    data:JSON.stringify({
                        "contributer_id":contributer_id,
                        "year":year_selected,
                        "change_type":"delete",
                        "user":global_user.uid
                    }),
                    success:function(res){
                        addNewAlert("success","Successfully Removed User, Changes may take a few minutes to propagate")
                    },
                    error:function(){
                        addNewAlert("error","Error Removing User, Please try again later")
                    }
                });
            });

        });
        $(".edit-contributer").off("click").click(function(){
            var contributer_id = $(this).parent().attr("id");
            contributer = year_obj[contributer_id];

            $(".edit-user-menu .name").val(contributer.name);
            $(".edit-user-menu .title").val(contributer.title);
            $(".edit-user-menu .description").val(contributer.description);
            $(".edit-user-menu .year").hide();
            $(".confirm-menu h2").text("Are you sure you would like to edit "+contributer.name+"?");
            displayEdit(function(){
                var file_input = document.querySelector(".picture");
                var reader = new FileReader();
                if(file_input.files[0] != null){
                    var name = file_input.files[0].name;
                    reader.readAsDataURL(file_input.files[0]);
                }
                
                var image = {url:"",ext:""};
                function sendData(){
                    $.ajax({
                        url:aws_api+"/EditContributer",
                        method:"POST",
                        data:JSON.stringify({
                            "contributer_id":contributer_id,
                            "year":year_selected,
                            "change_type":"edit",
                            "name":$(".edit-user-menu .name").val(),
                            "title":$(".edit-user-menu .title").val(),
                            "description":$(".edit-user-menu .description").val(),
                            "image":image,
                            "user":global_user.uid
                        }),
                        success:function(res){
                            addNewAlert("success","Successfully Edited User, Changes may take a few minutes to propagate")
                        },
                        error:function(){
                            addNewAlert("error","Error Editing User, Please try again later")
                        }
                    });
                }
                if($(".picture").val() != ""){
                    reader.onload = () => {
                        // Do something with the image data
                        image = {url:reader.result,ext:name.split(".").slice(-1)[0]};
                        sendData();
                    };
                } else{
                    sendData();
                }
                
                
                
            });

        });
        $("#add-new-contributer").off("click").click(function(){
            $(".confirm-menu h2").text("Are you sure you would like to add a new contributer?");
            $(".edit-user-menu .year").show();
            displayEdit(function(){
                var file_input = document.querySelector(".picture");
                var reader = new FileReader();
                if(file_input.files[0] != null){
                    var name = file_input.files[0].name;
                    reader.readAsDataURL(file_input.files[0]);
                }
                var image = {url:"",ext:""};
                function sendData(){
                    $.ajax({
                        url:aws_api+"/EditContributer",
                        method:"POST",
                        data:JSON.stringify({
                            "year":$(".edit-user-menu .year").val(),
                            "change_type":"add",
                            "name":$(".edit-user-menu .name").val(),
                            "title":$(".edit-user-menu .title").val(),
                            "description":$(".edit-user-menu .description").val(),
                            "image":image,
                            "user":global_user.uid
                        }),
                        success:function(res){
                            addNewAlert("success","Successfully Edited User, Changes may take a few minutes to propagate")
                        },
                        error:function(){
                            addNewAlert("error","Error Editing User, Please try again later")
                        }
                    });
                }
                if($(".picture").val() != ""){
                    reader.onload = () => {
                        // Do something with the image data
                        image = {url:reader.result,ext:name.split(".").slice(-1)[0]};
                        sendData();
                    };
                } else{
                    sendData();
                }
            });

        });
    }
    $.ajax({
        url:"/articles/editors.json",
        method:"GET",
        success:function(res){
            for(year of Object.keys(res).reverse()){
                $("#editor-year").append(`<option value="${year}">${year}</option>`)
            }
            $("#editor-year").on('change',function(){
                loadContributers($("#editor-year").val(),res[$("#editor-year").val()]);
            });
            loadContributers($("#editor-year").val(),res[$("#editor-year").val()]);
        }
    });
} else if(location.href.split("/").slice(-1)[0].split("?")[0]=="article.html"){
    $("")
}

function displayEdit(confirm){
    $(".edit-user-menu, .mask-background").css('opacity','1');
    $(".edit-user-menu, .mask-background").show();
    $(".confirm").off("click").click(function(){
        confirm();
        $(".edit-user-menu, .mask-background").css('opacity','0');
        $(".edit-user-menu, .mask-background").hide();
    });
    $(".deny").off("click").click(function(){
        $(".edit-user-menu, .mask-background").css('opacity','0');
        $(".edit-user-menu, .mask-background").hide();
    });
}


function displayConfirm(confirm){
    $(".confirm-menu, .mask-background").css('opacity','1');
    $(".confirm-menu, .mask-background").show();
    $(".confirm").off("click").click(function(){
        confirm();
        $(".confirm-menu, .mask-background").css('opacity','0');
        $(".confirm-menu, .mask-background").hide();
    });
    $(".deny").off("click").click(function(){
        $(".confirm-menu, .mask-background").css('opacity','0');
        $(".confirm-menu, .mask-background").hide();
    });
}

function onlyVerifiedUsers(){
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
          global_user = user;
          return user;
        } else {
          // No user is signed in.
          location.href="/";
        }
    });
}

if(["editor.html","list-articles.html","manage-users.html"].includes(location.href.split("/").slice(-1)[0].split("?")[0])){
    onlyVerifiedUsers();
}

$("#sign-in").on('submit',function(e){
    e.preventDefault();
    email = $("#si-email").val();
    password = $("#si-password").val();
    firebase.auth().signInWithEmailAndPassword(email, password).then(function(user) {
    }).catch(function(error) {
        addNewAlert("error","Error Signing in");
    });
});
$("#sign-up").on('submit',function(e){
    e.preventDefault();
    email = $("#su-email").val();
    password = $("#su-password").val();
    verifyPassword = $("#su-confirm-password").val();
    if(password == verifyPassword){
        firebase.auth().createUserWithEmailAndPassword(email, password).then(function(user) {
            createdUser = true;
        }).catch(function(error) {
        });
    }
});

function getGlobalUser(){
    return global_user;
}

function logout(){
    firebase.auth().signOut().then(() => {
        location.href ="/index.html";
    }).catch((error) => {
        // An error happened.
        alert("Error with signing out: "+error);
    });
}
