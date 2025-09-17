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
        const input = document.querySelector('#add-comment');
        if(button && input){
            const picker = new EmojiButton();
            picker.on('emoji', emoji => {
            input.value += emoji;
            });
            button.addEventListener('click', () => picker.togglePicker(button));
        }
    });
