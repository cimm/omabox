// Resizes the image to 800px (screen with of Raspberry Pi)
// and uploads the image to the Backblaze B2 bucket specified
// by the authorizationToken and uploadUrl.

async function upload(files, authorizationToken, uploadUrl) {
  spinner(true)

  const [ file ] = files
  const maxSize = 800

  await fetch(uploadUrl, {
    method: 'POST',
    headers: {
      'Authorization': authorizationToken,
      'X-Bz-File-Name': randomizeFilename(file),
      'X-Bz-Content-Sha1': 'do_not_verify'
    },
    body: await resizeImage(file, maxSize)
  })
  .then((response) => response.json())
  .then((data) => {
    spinner(false)
    document.getElementById('fileUpload').value = ''
    (data.action === 'upload') ? alert('Image uploaded') : alert('Oops, something went wrong')
  })
  .catch((error) => {
    spinner(false)
    alert(error)
  })
}

// Semi-randomizes the filename so we don't override 
// existing files in the bucket.
function randomizeFilename(file) {
  return Math.random().toString(36).substring(2) + '.' + file.name.split('.').pop()
}

function spinner(active) {
  let spin = document.getElementsByClassName('loader')[0]
  if (active) {
    spin.classList.add('is-active')
  } else {
    spin.classList.remove('is-active')
  }
}

// Resize image before uploading
// 1. Smaller uploads are better
// 2. imv has issues with very wide images
function resizeImage(file, maxSize) {
  const reader = new FileReader()
  const image = new Image()
  const canvas = document.createElement('canvas')

  const dataURItoBlob = function (dataURI) {
    const bytes = dataURI.split(',')[0].indexOf('base64') >= 0 ?
      atob(dataURI.split(',')[1]) :
      unescape(dataURI.split(',')[1])
    const mime = dataURI.split(',')[0].split(':')[1].split(';')[0]
    const max = bytes.length
    let ia = new Uint8Array(max)
    for (let i = 0; i < max; i++)
      ia[i] = bytes.charCodeAt(i)
    return new Blob([ia], { type: mime })
  }

  const resize = function () {
    let width = image.width
    let height = image.height
    if (width > height) {
      if (width > maxSize) {
        height *= maxSize / width
        width = maxSize
      }
    } else {
      if (height > maxSize) {
        width *= maxSize / height
        height = maxSize
      }
    }
    canvas.width = width
    canvas.height = height
    canvas.getContext('2d').drawImage(image, 0, 0, width, height)
    const dataUrl = canvas.toDataURL('image/jpeg')
    return dataURItoBlob(dataUrl)
  }

  return new Promise(function (ok, no) {
    if (!file.type.match(/image.*/)) {
      no(alert('Not an image'))
      return
    }
    reader.onload = function (readerEvent) {
      image.onload = function () { return ok(resize()) }
      image.src = readerEvent.target.result
    }
    reader.readAsDataURL(file)
  })
}
