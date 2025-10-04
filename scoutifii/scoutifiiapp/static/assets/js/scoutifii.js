const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie name begin with the name you want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const addPost = document.querySelector('#add_post');
const postUuid = Math.random().toString(36).slice(2,12)
jQuery(document).on('change', '#add_post', function(e){
    if ($('#feed-pic-upload').val()) {
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url  = $(this).attr('action');
        $.ajax({
            type: 'POST',
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(addPost),
            contentType: false,
            cache: false,
            processData:false,
            success: function(){                     
                toastr.success('Uploaded Successfully');
                window.location.reload("{% url 'dashboard' %}");
            },
            xhr: function() {                
                let xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", (evt) => {
                    if (evt.lengthComputable) {
                        let percent = Math.round(((evt.loaded / evt.total) * 100));
                        document.getElementById('progress_bar').style["display"] = 'block';

                        // let circle = document.querySelector('.circle-progress-bar');
                        // let circumference = 2 * Math.PI * 50;
                        // let offset = circumference - (percent / 100) * circumference;
                        // circle.style.strokeDashoffset = offset;

                            
                        document.getElementById('progress_bar_process').style["width"] = ""+percent + '%';
                        document.getElementById('progress_bar_process').innerHTML = ""+percent + '% completed';
                        document.getElementById('uploaded_video').innerHTML = "Uploaded:" + parseInt(evt.loaded/1000000)+"/"+parseInt(evt.total/1000000)+"MB";

                    }
                }, false);
                xhr.addEventListener('load', (event) =>{
                    document.getElementById('progress_bar').style["display"] = 'none';

                });
                    return xhr;
                },
            error: function(error){
                toastr.error("error");
            },
        });
        return false;
    }
});

/* For Autoplay of videos */
    const videos = document.querySelectorAll('video');

    // Play video when it is in view
    const playVideoInView = () => {
        for (const element of videos) {
            const video = element
            const rect = video.getBoundingClientRect();
            const isInView = (rect.top >= 0 && rect.bottom <= window.innerHeight);
            if (isInView) {
                video.play();
            } else {
                video.pause();
            }
        }
    };

    // Add event listener to window for scrolling and playing videos in view
    window.addEventListener('scroll', playVideoInView);
    window.addEventListener('resize', playVideoInView);
    window.addEventListener('load', playVideoInView);
    
    /* Make videos resume playing after ending */
    videos.forEach((video) => {
        video.addEventListener('ended', function() {
            this.currentTime = 0; // Reset the video to the beginning
            this.play(); // Play the video again
        });
    });

    /* End of Autoplay of videos */

    /* Start of Emojis */
    document.addEventListener('DOMContentLoaded', function() {
        const button = document.querySelector('#emoji-button');
        const input = document.querySelector('#create-comment');
        if(button && input){
            const picker = new EmojiButton();
            picker.on('emoji', (emoji) => {
                input.value += emoji;
            });
            button.addEventListener('click', () => picker.togglePicker(button));
        }
    });
/* End of Emojis */
/* Start of adding comments */
$(document).ready(function(){
    $('.create-comment').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action');
        
        $.ajax({
            method: "POST",
            url: url,
            headers: {
                "X-CSRFToken": csrftoken 
            },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(data){
                const dataArr = [];
                dataArr.push(data);
                toastr.success("Your comment counts");
            },
            error: function(error){
                toastr.error("error");
            }
        }); 
        document.querySelectorAll('input-comment').reset()             
    });
});
/* End of adding comments */

// THEME CUSTOMIZATION
        const theme = document.querySelector('#theme');
        const themeModal = document.querySelector('.customize-theme');
        const fontSizes = document.querySelectorAll('.choose-size span');
        const root = document.querySelector(':root');
        const colorPalette = document.querySelectorAll('.choose-color span');
        const Bg1 = document.querySelector('.bg-1');
        const Bg2 = document.querySelector('.bg-2');
        const Bg3 = document.querySelector('.bg-3');

        //opens modal
        const openThemeModal = () =>{
            themeModal.style.display = 'grid';
        }

        //closes modal
        const closeThemeModal = (e) =>{
            if(e.target.classList.contains('customize-theme')){
                themeModal.style.display = 'none';
            }
        }

        theme.addEventListener('click', openThemeModal);
        themeModal.addEventListener('click', closeThemeModal);

        // remove active class from spans or font size selectors
        const removeSizeSelector = () => {
            fontSizes.forEach(size => {
                size.classList.remove('active');
            })
        }

        // FONTS
         fontSizes.forEach(size => {
            size.addEventListener('click', () => {
                removeSizeSelector()
                let fontsize;
                size.classList.toggle('active');
                if(size.classList.contains('font-size-1')){
                    fontsize = '10px';
                    root.style.setProperty('----sticky-top-left', '5.4rem');
                    root.style.setProperty('----sticky-top-right', '5.4rem');
                } else if(size.classList.contains('font-size-2')){
                    fontsize = '13px';
                    root.style.setProperty('----sticky-top-left', '5.4rem');
                    root.style.setProperty('----sticky-top-right', '-7rem');
                } else if(size.classList.contains('font-size-3')){
                    fontsize = '15px';
                    root.style.setProperty('----sticky-top-left', '-2rem');
                    root.style.setProperty('----sticky-top-right', '-17rem');
                } else if(size.classList.contains('font-size-4')){
                    fontsize = '17px';
                    root.style.setProperty('----sticky-top-left', '5rem');
                    root.style.setProperty('----sticky-top-right', '-25rem');
                } else if(size.classList.contains('font-size-5')){
                    fontsize = '19px';
                    root.style.setProperty('----sticky-top-left', '-12rem');
                    root.style.setProperty('----sticky-top-right', '-33rem');
                }
                // change font sizes of html root element
                document.querySelector('html').style.fontSize = fontsize;
            })
         })

         // Remobe active class from colors
         const changeActiveColorClass = () => {
            colorPalette.forEach(colorPicker =>{
                colorPicker.classList.remove('active')
            })
         }

         //CHANGE COLOR BACKGROUND
         colorPalette.forEach(color =>{
            color.addEventListener('click', () => {
                let primary;
                changeActiveColorClass();
                if(color.classList.contains('color-1')){
                    primaryHue = 52;
                } else if(color.classList.contains('color-2')){
                    primaryHue = 252;
                } else if(color.classList.contains('color-3')){
                    primaryHue = 352;
                } else if(color.classList.contains('color-4')){
                    primaryHue = 152;
                } else if(color.classList.contains('color-5')){
                    primaryHue = 202;
                }
                color.classList.add('active')
                root.style.setProperty('--color-primary-hue', primaryHue)
            });
         })

         // theme background values
         let whiteColorLightness;
         let lightColorLightness;
         let darkColorLightness;

         // changes background color
         const changeBG = () =>{
            root.style.setProperty('--color-light-lightness', lightColorLightness);
            root.style.setProperty('--color-white-lightness', whiteColorLightness);
            root.style.setProperty('--color-dark-lightness', darkColorLightness);
         }

         Bg1.addEventListener('click', () =>{
            darkColorLightness = '252';
            whiteColorLightness = '100%';
            lightColorLightness = '90%';

            Bg1.classList.add('active');
            Bg2.classList.remove('active');
            Bg3.classList.remove('active');
            //remove customized changes from local storage
            //window.location.reload();
            changeBG();
         });

         Bg2.addEventListener('click', () =>{
            darkColorLightness = '95%';
            whiteColorLightness = '20%';
            lightColorLightness = '15%';

            Bg2.classList.add('active');
            Bg1.classList.remove('active');
            Bg3.classList.remove('active');
            changeBG();
         });

         Bg3.addEventListener('click', () =>{
            darkColorLightness = '95%';
            whiteColorLightness = '10%';
            lightColorLightness = '0%';

            Bg3.classList.add('active');
            Bg1.classList.remove('active');
            Bg2.classList.remove('active');
            changeBG();
         });



         /*Windows scroll  
        window.addEventListener('scroll', ()=>{
            document.querySelector('.profile-popup').style.display = 'none';
            document.querySelector('.add-post-popup').style.display = 'none';
        });*/

        // Sidebar
        const menuItems = document.querySelectorAll('.menu-item');

        const removeActiveItem = () => {
            menuItems.forEach(item =>{
                item.classList.remove('active');
            })
        }

        menuItems.forEach(item =>{
           item.addEventListener('click', () => { 
                removeActiveItem();
                item.classList.add('active');
            })  
        })


        // Active class remove
       const removeActive = ()=>{
            menuItem.forEach(item=>{
                item.classList.remove('active');
            });
        }

       // ..................Messages........................
       document.querySelector('#messageMenu').addEventListener('click', ()=>{
            document.querySelector('#notifyCounter2').style.display = 'none';
            document.querySelector('.messages').classList.toggle('boxshadow1');
            setTimeout(()=>{                
                document.querySelector('.messages').classList.remove('boxshadow1');
            }, 300);
       });


// ...................Comments Modal Start..........................
const commentTriggers = document.querySelectorAll('.comment-button');
const commentModals = document.querySelectorAll('.comment-section');

// open the comment modal for the corresponding feed
const openCommentModal = (trigger) => {
    const feed = trigger.closest('.feed');
    const modal = feed ? feed.querySelector('.comment-section') : null;
    if (modal) {
        modal.style.display = 'grid';
    }
};

// close when clicking on the overlay background
const closeCommentModal = (trigger) => {
    if (e.target.classList.contains('comment-section')) {
        e.target.style.display = 'none';
    }
};

// attach events for all triggers
commentTriggers.forEach((trigger) => {
    // mouse click
    trigger.addEventListener('click', () => openCommentModal(trigger));
});

// attach close handler to each modal
commentModals.forEach((modal) => {
    modal.addEventListener('click', closeCommentModal);
});


// ...................Comments Modal End..........................

// ...............Start of Like button.......................

// $(document).ready(function(){
//     $('.like__form').on('submit', function(e){
//         e.preventDefault();

//         const $form = $(this);
//         const $btn = $form.find('like-button');
//         const csrftoken = getCookie('csrftoken');
//         const url = $form.attr('action');
        
//         $btn.toggleClass('is-liked');

//         $.ajax({
//             method: "POST",
//             url: url,
//             headers: {"X-CSRFToken": csrftoken },
//             data: new FormData(this),
//             contentType: false,
//             cache: false,
//             processData:false,
//             success: function(response){
//                 if(response && typeof response.liked !== 'undefined'){
//                     $btn.toggleClass('is-liked', !!response.liked);
//                 }
//                 toastr.success("You Liked");
//             },
//             error: function(error){
//                 $btn.toggleClass('is-liked');
//                 toastr.error("error");
//             },
//         });
//     });
// });
// End of Like button
// Start of flair button
$(document).ready(function(){
    $('.flair__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Flair Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});
// End of flair button

$(document).ready(function(){
    $('.positioning__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Positioning Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.marking__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Marking Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.tackling__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Tackling Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});
   
$(document).ready(function(){
    $('.vision__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Vision Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.pace__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Pace Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.speed__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Speed Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.heading__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Heading Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.jumping-reach__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Jumping Reach Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.work-rate__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Workrate Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.aggression__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Aggression Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.charisma__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Charisma Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.ball_protection__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Ball Protection Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.crossing__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Crossing Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.shooting__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Shooting Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.technique__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Technique Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.passing__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Passing Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.finishing__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Finishing Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.ball-control__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Ball Control Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.shooting__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Shooting Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.free-kick__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("FreeKick Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});

$(document).ready(function(){
    $('.dribbling__form').submit(function(e){
        e.preventDefault();
        const csrftoken = getCookie('csrftoken');
        const url = $(this).attr('action')

        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken },
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                toastr.success("Dribbling Ticked");
            },
            error: function(error){
                toastr.error("error");
            }
        });
    });
});


// utils
function pluralize(n, one, many) {
  return Number(n) === 1 ? one : many;
}

async function fetchCounts(postId) {
  const res = await fetch(`post/${encodeURIComponent(postId)}`, { credentials: 'same-origin' });
  if (!res.ok) throw new Error('Failed to fetch counts');
  return res.json();
}

function updateCountersInDom(postId, data) {
  const likeEl = document.querySelector(`[data-like-counter="${postId}"]`);
  const likeLabel = document.querySelector(`[data-like-label="${postId}"]`);
  const viewEl = document.querySelector(`[data-view-counter="${postId}"]`);
  const viewLabel = document.querySelector(`[data-view-label="${postId}"]`);
  const commentEl = document.querySelector(`[data-comment-counter="${postId}"]`);
  const commentLabel = document.querySelector(`[data-comment-label="${postId}"]`);

  if (likeEl) likeEl.textContent = data.likes;
  if (likeLabel) likeLabel.textContent = pluralize(data.likes, 'Like', 'Likes');
  if (viewEl) viewEl.textContent = data.views;
  if (viewLabel) viewLabel.textContent = pluralize(data.views, 'view', 'views');
  if (commentEl) commentEl.textContent = data.comments;
  if (commentLabel) commentLabel.textContent = pluralize(data.comments, 'Comment', 'Comments');
}

function collectVisiblePostIds() {
  return Array.from(document.querySelectorAll('.interaction-button[data-post-id]'))
    .map(el => Number(el.getAttribute('data-post-id')))
    .filter(Boolean);
}

// Periodic refresh (e.g., every 15s)
function startCountsPolling(intervalMs = 15000) {
  const postIds = collectVisiblePostIds();
  if (!postIds.length) return;

  async function tick() {
    for (const id of postIds) {
      try {
        const data = await fetchCounts(id);
        updateCountersInDom(id, data);
      } catch (e) {
        // optionally log
      }
    }
  }
  tick(); // initial
  return setInterval(tick, intervalMs);
}
// JavaScript
$(document).on('submit', '.like__form', function (e) {
  e.preventDefault();
  const $form = $(this);
  const url = $form.attr('action');
  const csrftoken = getCookie('csrftoken');
  const fd = new FormData(this);

  // Try to get post id from hidden input or data attribute
  let postId = Number($form.find('input[name="post_id"]').val());
  if (!postId) {
    postId = Number($form.data('postId')) || Number($form.closest('[data-post-id]').data('postId'));
  }

  // Button class must match your DOM, ensure it is ".like-button"
  const $btn = $form.find('.like-button');
  const revertOnError = $btn.length > 0;

  // Optimistic UI
  if (revertOnError) $btn.toggleClass('is-liked');

  $.ajax({
    method: 'POST',
    url,
    headers: { 'X-CSRFToken': csrftoken },
    data: fd,
    contentType: false,
    cache: false,
    processData: false,
    success: async function (response) {
      // Sync liked state if provided
      if ($btn.length && typeof response?.liked !== 'undefined') {
        $btn.toggleClass('is-liked', !!response.liked);
      }

      // Update counters
      if (postId) {
        if (typeof response?.likes !== 'undefined') {
          updateCountersInDom(postId, {
            likes: response.likes,
            views: response.views ?? Number(document.querySelector(`[data-view-counter="${postId}"]`)?.textContent) ?? 0,
            comments: response.comments ?? Number(document.querySelector(`[data-comment-counter="${postId}"]`)?.textContent) ?? 0,
          });
        } else {
          try {
            const data = await fetchCounts(postId);
            updateCountersInDom(postId, data);
          } catch (_) { /* ignore */ }
        }
      }
    },
    error: function () {
      if (revertOnError) $btn.toggleClass('is-liked'); // revert optimistic toggle
      toastr.error('Could not like. Please try again.');
    },
  });
});






// Hook like__form success to refresh immediately
// $(document).ready(function () {
//   // Start polling
//   startCountsPolling(15000);

//   // Enhance existing like form handler if present
//   $('.like__form').on('submit', function (e) {
//     e.preventDefault();
//     const $form = $(this);
//     const url = $form.attr('action');
//     const csrftoken = getCookie('csrftoken'); // your existing helper
//     const postId = Number($form.find('input[name="post_id"]').val());

//     // optimistic UI toggle if you implemented .is-liked
//     const $btn = $form.find('.like-button');
//     $btn.toggleClass('is-liked');

//     $.ajax({
//       method: 'POST',
//       url,
//       headers: { 'X-CSRFToken': csrftoken },
//       data: new FormData(this),
//       contentType: false,
//       cache: false,
//       processData: false,
//       success: async function (response) {
//         // If backend returns liked and likes, use it; otherwise query counts endpoint
//         if (response && typeof response.likes !== 'undefined') {
//           updateCountersInDom(postId, {
//             likes: response.likes,
//             views: response.views ?? document.querySelector(`[data-view-counter="${postId}"]`)?.textContent ?? 0,
//             comments: response.comments ?? document.querySelector(`[data-comment-counter="${postId}"]`)?.textContent ?? 0,
//           });
//         } else {
//           try {
//             const data = await fetchCounts(postId);
//             updateCountersInDom(postId, data);
//           } catch {}
//         }
//         // sync liked state if server sent it
//         if (response && typeof response.liked !== 'undefined') {
//           $btn.toggleClass('is-liked', !!response.liked);
//         }
//       },
//       error: function () {
//         // revert optimistic toggle on error
//         $btn.toggleClass('is-liked');
//       },
//     });
//   });
// });


document.addEventListener('DOMContentLoaded', () => {
  const fallbackModal = document.getElementById('share-fallback');
  const shareInput = document.getElementById('share-url-input');
  const copyBtn = document.getElementById('copy-share-url');
  const closeBtn = document.getElementById('close-share-fallback');

    function openFallback(url) {
        if (!fallbackModal) return;
        shareInput.value = url;
        fallbackModal.classList.remove('hidden');
        shareInput.focus();
        shareInput.select();
    }

    function closeFallback() {
        if (!fallbackModal) return;
        fallbackModal.classList.add('hidden');
    }

    document.querySelectorAll('.share-button').forEach(btn => {
        btn.addEventListener('click', async () => {
        const title = btn.dataset.shareTitle || 'Share';
        const text = btn.dataset.shareText || '';
        const url = btn.dataset.shareUrl || window.location.href;

        if (navigator.share) {
            try {
            await navigator.share({ title, text, url });
            } catch (err) {
            // User canceled or share failed; silently ignore or open fallback
            // openFallback(url);
            }
        } else {
            // Fallback: try clipboard, else open modal
            try {
            await navigator.clipboard.writeText(url);
            alert('Link copied to clipboard');
            } catch (_) {
            openFallback(url);
            }
        }
        });
    });

    copyBtn?.addEventListener('click', async () => {
        try {
        await navigator.clipboard.writeText(shareInput.value);
        copyBtn.textContent = 'Copied!';
        setTimeout(() => (copyBtn.textContent = 'Copy'), 1500);
        } catch (_) {
        // no-op
        }
    });

    closeBtn?.addEventListener('click', closeFallback);
    fallbackModal?.addEventListener('click', (e) => {
        if (e.target === fallbackModal) closeFallback();
    });
});

// .........Repost: open modal with selected post id
document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('repost-modal');
  const form = document.getElementById('repost-form');
  const originalInput = document.getElementById('repost-original-id');
  const msgInput = document.getElementById('repost-message');
  const cancelBtn = document.getElementById('repost-cancel');

  function openRepostModal(postId) {
    originalInput.value = String(postId);
    msgInput.value = '';
    modal.classList.remove('hidden');
    msgInput.focus();
  }
  function closeRepostModal() {
    modal.classList.add('hidden');
  }

  document.querySelectorAll('.repost-button').forEach(btn => {
    btn.addEventListener('click', () => {
      const postId = btn.getAttribute('data-post-id');
      openRepostModal(postId);
    });
  });

  cancelBtn?.addEventListener('click', closeRepostModal);
  modal?.addEventListener('click', (e) => {
    if (e.target === modal) closeRepostModal();
  });

  // Submit AJAX
  $('.repost__form').on('submit', function(e) {
    e.preventDefault();
    const csrftoken = getCookie('csrftoken');
    const url = $(this).attr('action');
    const fd = new FormData(this);

    $.ajax({
      method: 'POST',
      url,
      headers: { 'X-CSRFToken': csrftoken },
      data: fd,
      contentType: false,
      cache: false,
      processData: false,
      success: function(resp) {
        toastr.success('Shared to your timeline');
        // Optional: update a counter in DOM if you show repost counts
        const postId = resp.original_id;
        const counter = document.querySelector(`[data-repost-counter="${postId}"]`);
        const label = document.querySelector(`[data-repost-label="${postId}"]`);
        if (counter && typeof resp.repost_count !== 'undefined') {
          counter.textContent = resp.repost_count;
          if (label) label.textContent = Number(resp.repost_count) === 1 ? 'Share' : 'Shares';
        }
        // Optimistic: optionally prepend the new repost to the feed list if available
        closeRepostModal();
      },
      error: function() {
        toastr.error('Could not share. Please try again.');
      },
    });
  });
});

// ..............Toggle password.............
function loginPassword(){
    const password = document.getElementById("loginpassword");
    if (password.type == "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}

function signupPassword(){
    const password = document.getElementById("signuppassword");
    if (password.type == "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}

function confirmPassword(){
    const password = document.getElementById("confirmpassword");
    if (password.type == "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}

