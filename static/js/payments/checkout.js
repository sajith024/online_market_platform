document.addEventListener("DOMContentLoaded", async () => {
  let elements;

  const response = await fetch(
    "http://127.0.0.1:8000/api/payments/stripe_config/"
  );

  const responseData = await response.json();
  const { publishableKey } = responseData.data;
  const stripe = Stripe(publishableKey);

  const paymentForm = document.querySelector("#payment-form");
  paymentForm.addEventListener("submit", handleSubmit);
  const orderId = paymentForm.getAttribute("data-order-id");

  initialize();
  checkStatus();

  async function initialize() {
    const response = await fetch(
      "http://127.0.0.1:8000/api/payments/create_payment/",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ order_id: orderId }),
      }
    );

    const responseData = await response.json();
    const { clientSecret } = responseData.data;

    const appearance = {
      theme: "stripe",
    };
    elements = stripe.elements({ appearance, clientSecret });

    const paymentElementOptions = {
      layout: "tabs",
    };

    const paymentElement = elements.create("payment", paymentElementOptions);
    paymentElement.mount("#payment-element");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: "http://localhost:8000/payments/success/",
      },
    });

    console.log(error);
    if (error.type === "card_error" || error.type === "validation_error") {
      showMessage(error.message);
    } else {
      showMessage("An unexpected error occurred.");
    }

    setLoading(false);
  }

  async function checkStatus() {
    const clientSecret = new URLSearchParams(window.location.search).get(
      "payment_intent_client_secret"
    );

    if (!clientSecret) {
      return;
    }

    const { paymentIntent } = await stripe.retrievePaymentIntent(clientSecret);

    switch (paymentIntent.status) {
      case "succeeded":
        showMessage("Payment succeeded!");
        break;
      case "processing":
        showMessage("Your payment is processing.");
        break;
      case "requires_payment_method":
        showMessage("Your payment was not successful, please try again.");
        break;
      default:
        showMessage("Something went wrong.");
        break;
    }
  }

  function showMessage(messageText) {
    const messageContainer = document.querySelector("#payment-message");

    messageContainer.classList.remove("hidden");
    messageContainer.textContent = messageText;

    setTimeout(function () {
      messageContainer.classList.add("hidden");
      messageContainer.textContent = "";
    }, 4000);
  }

  function setLoading(isLoading) {
    if (isLoading) {
      document.querySelector("#submit").disabled = true;
      document.querySelector("#spinner").classList.remove("hidden");
      document.querySelector("#button-text").classList.add("hidden");
    } else {
      document.querySelector("#submit").disabled = false;
      document.querySelector("#spinner").classList.add("hidden");
      document.querySelector("#button-text").classList.remove("hidden");
    }
  }
});
