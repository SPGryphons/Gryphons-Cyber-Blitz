const show_message = (msg) => {
  $('.error').css('display', 'block')

  if (msg) {
    $('.error').html(msg)
  }

  setTimeout(() => {
      $('.error').css('display', 'none')
  }, 10000)
}

const get_post = () => {
  let post_link = window.location.href.split('/')[4];

  fetch(`/api/view/${post_link}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(res => {
    if (res.status === 200) {
      res.json().then(data => {
        $('#post-title').text(data['title']);
        $('#post-content').html(data['content'].replace(/(?:\r\n|\r|\n)/g, '<br>')); 
      })
    } else {
      res.json().then(data => {
        show_message(data['error']);
      })
    }
  }).catch((err) => {
    if (err) {
      console.log(err);
    }
  })
}