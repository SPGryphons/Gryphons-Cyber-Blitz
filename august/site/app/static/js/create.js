const show_message = (msg) => {
  $('.error').css('display', 'block')

  if (msg) {
    $('.error').html(msg)
  }

  setTimeout(() => {
      $('.error').css('display', 'none')
  }, 10000)
}

const create = () => {
  let question = $('#title').val();
  let answer = $('#content').val();

  if (!question || !answer) {
    show_message('Please fill in all fields');
    return;
  }

  fetch('/api/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        'title': question,
        'content': answer
    })
  })
  .then(res => {
    if (res.status === 200) {
      if (res.url.includes('login')){ 
        window.location.replace('/login')
      }
      res.json().then(data => {
        window.location.replace('/view/' + data['link'])
      })
    } else if (res.status === 429){
      show_message('Too many requests. Please try again later.');
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