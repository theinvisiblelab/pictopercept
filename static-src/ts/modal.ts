class ActionButton {
	readonly text: string;
	readonly action: () => void;

	constructor(text: string, action: () => void) {
		this.text = text;
		this.action = action;
	}
}

class Modal {
	private title: string;
	private message: string;
	private buttons: ActionButton[];

	constructor(title: string, message: string, buttons: ActionButton[]) {
		this.title = title;
		this.message = message;
		this.buttons = buttons;

		this.initialize();
	}

	initialize() {
		const outerElement = document.createElement("div");
		outerElement.classList.add("modal-outer");

		const modalElement = document.createElement("div")
		modalElement.classList.add("modal");

		const titleElement = document.createElement("div");
		titleElement.classList.add("title");
		titleElement.innerText = this.title;

		const bodyElement = document.createElement("div");
		bodyElement.classList.add("body");
		bodyElement.innerText = this.message;

		const buttonsElement = document.createElement("div");
		buttonsElement.classList.add("buttons");


		this.buttons.forEach((actionButton) => {
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
		// modalDiv.classList.add("modal");

		// const div = document.createElement("div")
		// const modalElement = `
		// 	<div class="modal">
		// 		<div class="title">${this.title}</div>
		// 		<div class="body">${this.message}</div>
		// 		<div class="buttons">
		// 			<button>Button one</button>
		// 			<button>Button two</button>
		// 		</div>
		// 	</div>
		// `;

		// document.append("hi");
	}
}
