fetch("/purchase/stripe-config/")
.then((result) => { return result.json(); })
.then((data) => {
  const stripe = Stripe(data.publicKey);
  const purchaseButtonList = document.getElementsByClassName("purchase-btn")
  for (let i = 0; i < purchaseButtonList.length; i++){
    let currentButton = purchaseButtonList[i];
    let planId = currentButton.id;
    currentButton.addEventListener("click", () => {
        fetch("/checkout-session/", {
            method: "POST",
            body: JSON.stringify({ plan_id: planId}),
            headers: new Headers({'content-type': 'application/json'}),
        })
        .then((result) => { return result.json(); })
        .then((data) => {
          console.log(data);
          // Redirect to Stripe Checkout
          return stripe.redirectToCheckout({sessionId: data.sessionId})
        })
        .then((res) => {
          console.log(res);
        });
    })
  }
});