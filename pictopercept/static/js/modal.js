/**
 * An action button.
 */
class ActionButton {
	/**
	* @type {string}
	*/
	text;
	// readonly text: string;
	/**
	* @type {() => void}
	*/
	// readonly action: () => void;
	action;

	/**
	* Creates a new ActionButton.
	* @param {string} text - The text to show in the button.
	* @param {() => void} action - The function to execute when pressing the button.
	*/
	constructor(text, action) {
		this.text = text;
		this.action = action;
	}
}

/*
 * A modal.
 */
class Modal {
	/**
	 * The title of the modal.
	 * @type {string}
	 */
	#title;

	/**
	 * The body text of the modal.
	 * @type {string}
	 */
	#message;

	/**
	 * The body text of the modal.
	 * @type {ActionButton[]} - The available buttons in the modal.
	 */
	#buttons;

	/**
	 * Creates a new Modal.
	 * @param {string} title - The title of the modal.
	 * @param {string} message - The body text of the modal.
	 * @param {ActionButton[]} buttons - The available buttons in the modal.
	 */
	constructor(title, message, buttons) {
		this.#title = title;
		this.#message = message;
		this.#buttons = buttons;

		this.initialize();
	}

	initialize() {
		const outerElement = document.createElement("div");
		outerElement.classList.add("modal-outer");

		const modalElement = document.createElement("div")
		modalElement.classList.add("modal");

		const titleElement = document.createElement("div");
		titleElement.classList.add("title");
		titleElement.innerText = this.#title;

		const bodyElement = document.createElement("div");
		bodyElement.classList.add("body");
		bodyElement.innerHTML = this.#message;

		const buttonsElement = document.createElement("div");
		buttonsElement.classList.add("buttons");


		this.#buttons.forEach((actionButton) => {
			const buttonElement = document.createElement("button");
			buttonElement.innerText = actionButton.text;

			buttonElement.addEventListener("click", actionButton.action)
			buttonsElement.appendChild(buttonElement);
		})

		modalElement.appendChild(titleElement);
		modalElement.appendChild(bodyElement);
		modalElement.appendChild(buttonsElement);

		outerElement.appendChild(modalElement);

		document.body.appendChild(outerElement);
	}
}
