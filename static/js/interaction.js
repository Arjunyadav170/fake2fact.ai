
const input_desin=document.querySelectorAll('.input_desin button');
const inputArea=document.getElementById('input_area');
const claimInput = document.getElementById('claim_input');
const fact_check_button=document.getElementById('fact_check_button');
const result=document.getElementById('result');
const clean_text=document.querySelector('.clear_button');


input_desin.forEach(tab=>{
    tab.addEventListener('click',()=>{
        input_desin.forEach(t=>t.classList.remove('active'));
        tab.classList.add('active');
        const type = tab.dataset.tab;
        if (type === 'text_button') {
            inputArea.innerHTML = '<textarea id="claim_input" rows="4" placeholder="Enter the claim you want to verify..."></textarea> <div>Example: "COVID vaccines contain microchips"</div>';
          } else if (type === 'url_button') {
            inputArea.innerHTML = '<input type="url" id="claim_input" placeholder="Paste article URL...">';
          } else if (type === 'image_button') {
            inputArea.innerHTML = '<p>Image upload feature coming soon.</p>';
          } else if (type === 'audio_button') {
            inputArea.innerHTML = '<p>Audio upload feature coming soon.</p>';
          }
        });
      });

fact_check_button.addEventListener('click',()=>{
  const inputText = document.getElementById('claim_input').value;
  const activeTab = document.querySelector('.input_desin button.active');
  const inputType = activeTab ? activeTab.dataset.tab : 'text_button';
  if(!inputText) return;
  result.style.display = "block";
  result.innerHTML='<p>Verifying...</p>';
  // send data to flask application
  fetch( '/claim_checking',{
     method:'POST',
      headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      input_type: inputType,
      claim: inputText
      })

  })
 .then(res => res.json())
 .then(data => {
  if (!data.result || data.result.length === 0) {
    result.innerHTML = "<p>No relevant articles found.</p>";
    return;
  }

  let formattedHTML = "";

  data.result.forEach((item, index) => {
    formattedHTML += `
      <div class="result-item" style="margin-bottom:15px; padding:10px; border:1px solid #ddd; border-radius:8px;">
        <h3>${index + 1}. ${item.title || "No Title"}</h3>
        <p><strong>Source:</strong> ${item.source || "Unknown"}</p>
        <p><strong>Published:</strong> ${item.published || "N/A"}</p>
        <p><strong>Short Summary:</strong> ${item.short_summary || "N/A"}</p>
        <p><strong>Final Summary:</strong> ${item.final_summary || "N/A"}</p>
        <a href="${item.link}" target="_blank">Read more</a>
      </div>
    `;
  });

  result.innerHTML = formattedHTML;
})

 .catch(err => {
    result.innerHTML = `<p style="color:red;">Error verifying claim.</p>`;
    console.error(err);
 });

});    

clean_text.addEventListener('click',()=>{
  const claimInput = document.getElementById('claim_input');
  if (claimInput) claimInput.value = '';
  result.innerHTML = '';
  result.style.display="none";
});


