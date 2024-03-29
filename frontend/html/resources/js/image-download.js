// ************************ Drag and drop ***************** //
let dropArea = document.getElementById("drop-area")

  // Prevent default drag behaviors
  ;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false)
    document.body.addEventListener(eventName, preventDefaults, false)
  })

  // Highlight drop area when item is dragged over it
  ;['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false)
  })

  ;['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false)
  })

// Handle dropped files
dropArea.addEventListener('drop', handleDrop, false)

function preventDefaults(e) {
  e.preventDefault()
  e.stopPropagation()
}

function highlight(e) {
  dropArea.classList.add('highlight')
}

function unhighlight(e) {
  dropArea.classList.remove('highlight')
}

function handleDrop(e) {
  var dt = e.dataTransfer
  var files = dt.files

  handleFiles(files)
}

let uploadProgress = []
let progressBar = document.getElementById('progress-bar')

function initializeProgress(numFiles) {
  progressBar.value = 0
  uploadProgress = []

  for (let i = numFiles; i > 0; i--) {
    uploadProgress.push(0)
  }
}

function updateProgress(fileNumber, percent) {
  uploadProgress[fileNumber] = percent
  let total = uploadProgress.reduce((tot, curr) => tot + curr, 0) / uploadProgress.length
  progressBar.value = total
}

function handleFiles(files) {
  files = [...files]
  initializeProgress(files.length)
  files.forEach(uploadFile)
  files.forEach(previewFile)
}

function previewFile(file) {
  let reader = new FileReader()
  reader.readAsDataURL(file)
  reader.onloadend = function () {
    let img = document.createElement('img')
    img.src = reader.result
    document.getElementById('gallery').appendChild(img)
  }
}

async function createSession(patient_id, photo_id) {
  const url = `http://0.0.0.0:8001/predict_session/`;
  await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      patient_id: patient_id,
      photo_id: photo_id,
      predict_score: 0,
      start_datetime: Date.now()
    })
  })
    .then(async response => {
      if (response.status !== 200) {
        throw new Error('Произошла ошибка при создании сессии!');
      }
      return await response.json()
    })
    .then(async response => {
      sessionStorage.setItem('predict_session_id', response.id);
    })
    .catch(error => {
      alert(error.message)
    });
}

async function uploadFile(file, i) {
  const patient_id = sessionStorage.getItem("userId");
  const url = `http://0.0.0.0:8001/patient/${patient_id}/upload`;
  const xhr = new XMLHttpRequest()
  const formData = new FormData()
  xhr.open('POST', url, true)
  const token = 'Bearer ' + sessionStorage.getItem('token')
  xhr.setRequestHeader('Authorization', token);

  // Update progress (can be used to show progress indicator)
  xhr.upload.addEventListener("progress", function (e) {
    updateProgress(i, (e.loaded * 100.0 / e.total) || 100)
  })

  xhr.addEventListener('readystatechange', async function (e) {
    if (xhr.readyState == 4 && xhr.status == 200) {
      updateProgress(i, 100)
      let photo_id = xhr.responseText;
      await createSession(patient_id, photo_id)
      window.location.replace("http://0.0.0.0:3001/analysis-result")
    } else if (xhr.readyState == 4 && xhr.status != 200) {
      alert("Ошибка загрузки на сервер! Перезагрузите страницу!")
    }
  })

  formData.append('file', file)
  xhr.send(formData)
}