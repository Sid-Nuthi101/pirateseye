var aws_api = "https://z6g7kdihxe.execute-api.us-east-1.amazonaws.com/Prod";

function loadManifest(loadSite){
    $.ajax({
        dataType: "json",
        url:"/index_manifest.json",
        method:"GET",
        success:loadSite
    });
}

function highTilt(item){
    var options = {
        maxTilt:7,
        glare: true,
        maxGlare: 1
    };
    var tilt_immersive = $(item).tilt(options);
    options.maxTilt = 11;
}

function truncateString(str, length) {
    try {
        if(length == 0){
            return "";
        }
        if (str.length > length) {
            return str.slice(0, length) + '...';
        }
        
    } catch (error) {
    }
    return str;
}
function pushAlert(a , b){
    addNewAlert(a,b);
}

//Check if a specific draft is being requested
function getQueryParam(param) {
    const searchParams = new URLSearchParams(window.location.search);
    return searchParams.get(param);
}

function makeid(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
      counter += 1;
    }
    return result;
}
var text_element = 0;
function loadText(text, element){
    var continueB = "";
    var continueI = "";
    for(word of text.split(" ")){
        if(word.includes("*b*") || continueB != ""){
            text_element_id = "te-"+text_element;
            if(continueB == ""){
                $(element).append(`<span id="${text_element_id}"></span>`);
                word_split = word.split("");
                
                //Text before split
                starter = word.search("/*b/*");
                $("#"+text_element_id).append("<span class='before'></span>");
                $("#"+text_element_id+" .before").text(word_split.slice(0,starter-1).join(""));
                
                //Text during split
                end = word.search(/\*\/b\*/i);
                if(end != -1){
                    $("#"+text_element_id).append("<span class='during'><b></b> </span>");
                    $("#"+text_element_id+" .during b").text(word_split.slice(starter+2,end).join(""));
                    $("#"+text_element_id).append("<span class='after'></span>");
                    $("#"+text_element_id+" .after").text(word_split.slice(end+4).join(""));
                    text_element++;
                } else{
                    continueB = word_split.slice(starter+2).join("") +" ";
                }
            } else{
                end = word.search(/\*\/b\*/i);
                word_split = word.split("");
                if(end != -1){
                    $("#"+text_element_id).append("<span class='during'><b></b> </span>");
                    $("#"+text_element_id+" .during b").text(continueB + word_split.slice(0,end).join("")+" ");
                    $("#"+text_element_id).append("<span class='after'></span>");
                    $("#"+text_element_id+" .after").text(word_split.slice(end+4).join("") + " ");
                    continueB = "";
                    text_element++;
                } else{
                    continueB += word+" ";
                }
            }
            

            // applyTextStyles(word, "te-"+text_element);
        } else if(word.includes("*i*")){
            text_element_id = "te-"+text_element;
            $(element).append(`<span id="${text_element_id}"></span>`);
            word_split = word.split("");
            
            //Text before split
            starter = word.search("/*i/*");
            $("#"+text_element_id).append("<span class='before'></span>");
            $("#"+text_element_id+" .before").text(word_split.slice(0,starter-1).join(""));
            
            //Text during split
            end = word.search("/*//i/*");
            console.log(word_split.slice(starter+2,end-3).join(""));
            $("#"+text_element_id).append("<span class='during'><i></i> </span>");
            $("#"+text_element_id+" .during i").text(word_split.slice(starter+2,end-3).join(""));
            

            // applyTextStyles(word, "te-"+text_element);
        } else{
            $(element).append(`<span id="te-${text_element}"></span>`);
            $("#te-"+text_element).text(word+" ");
            text_element++;
        }
    }
}

//Apply the styles for bolding, italicizing, etc.
function applyTextStyles(text){
    text = text.replaceAll("*b*","<b>");
    text = text.replaceAll("*/b*","</b>");
    text = text.replaceAll("*i*","<i>");
    text = text.replaceAll("*/i*","</i>");

    //Links
    text = text.replace(/\*link to='(.*?)'\*(.*?)\*\/link\*/g, "<a href='$1'>$2</a>");
    return text;
}
document.body.innerHTML += "<div class='alerts_box'></div>";
var alert_id = 0;
function dissapear(item) {
    item.addClass("hide-opacity");
    setTimeout(function () {
        item.remove();
    }, 1000)
}
function addNewAlert(type, content) {
    $('.alerts_box').prepend(`
        <div class="alert alert-${type} alert-dismissible" role="alert" id="box-${alert_id}">
            ${content}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
    </div>`);
    item = $("#box-" + alert_id);
    setTimeout(dissapear, 4000, item);

    $(".close").click(function () {
        dissapear(item);
    });
    alert_id += 1;
}

if(["manage-users.html","list-articles.html","editor.html"].includes(location.href.split("/").slice(-1)[0].split("?")[0])){
    var navbar = `<div class="navbar">
        <a class="navbar-brand" href="/"><img src="/images/pirate.png"/></a>
        <div class="links">
            <a class="navbar-brand" href="/"><span class="newsletter-name">The Pirate's Eye</span></a>
            <div class="extention-links">
                <a href="/articles/list-articles.html">List Articles</a>
                <a href="/manage-users.html">Manage Users</a>
                <a href="/logout.html">Logout</a>
            </div>
        </div>
        <button class="collapse-navbar">Collapse</button>
    </div>
    `;
    $("body").prepend(navbar);
}else{
    links = `>
    `;
    var navbar = `<div class="navbar">
        <a class="navbar-brand" href="/"><img src="/images/pirate.png"/></a>
        <div class="links">
            <a class="navbar-brand" href="/"><span class="newsletter-name">The Pirate's Eye</span></a>
            <div class="extention-links">
                <a href="/section.html?section=news">News</a>
                <a href="/section.html?section=culture">Culture</a>
                <a href="/section.html?section=opinion">Opinion</a>
                <a href="/section.html?section=sports">Sports</a>
                <a href="/section.html?section=student-resources">Student Resources</a>
                <a href="/about.html">About</a>
            </div>
        </div>
        <button class="collapse-navbar"><i class="fa fa-bars"></i></button>
    </div>
    `;
    var popup = `
        <div class="popup">
        <div class="extention-links">
            <a href="/section.html?section=news">News</a>
            <a href="/section.html?section=culture">Culture</a>
            <a href="/section.html?section=opinion">Opinion</a>
            <a href="/section.html?section=sports">Sports</a>
            <a href="/section.html?section=student-resources">Student Resources</a>
            <a href="/about.html">About</a>
            <p id="close-navbar">Close</p>
        </div>
        </div>
    `;
    var footer = `
        <div class = "footer">
            <div style="display:flex">
                <img src="/images/pirate.png"/><span class="newsletter-name">The Pirate's Eye</span>
            </div>
            <a href="/login.html">Editor Login</a>
            <p>Email us at: <a href="mailto:pirates.eye@gmail.com">pirates.eye@gmail.com</a></p>
        </div>
    `;
    $("body").append(footer);
    $("body").append(popup);
    $("body").prepend(navbar);
    var showing = false;
    $(".collapse-navbar, #close-navbar").click(function(){
        if(!showing){
            $(".popup").addClass("popup-showing");
        } else{$(".popup").removeClass("popup-showing");}
        showing = !showing;
        
    })
}
$("head").append(`<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">`);
function capitalizeFirst(mySentence){
    var words = mySentence.split(" ");

    for (let i = 0; i < words.length; i++) {
        words[i] = words[i][0].toUpperCase() + words[i].substr(1);
    }

    var words = words.join(" ").split("-");

    for (let i = 0; i < words.length; i++) {
        words[i] = words[i][0].toUpperCase() + words[i].substr(1);
    }

    return words.join(" ");
}

function caseify(str) {
    str = str.replace(/[^\w]/g, "-");
    return str.replace(/ /g, "-");
}

function getCurrentAcademicYear() {
    const currentDate = new Date();
    const currentMonth = currentDate.getMonth();
    const currentYear = currentDate.getFullYear();
    const academicYear = currentMonth < 6 ? currentYear - 1 : currentYear;
    return academicYear;
}