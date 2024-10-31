class GeneratedQuestion {
	readonly text: string;
	readonly variables: { [key: string]: string }

	constructor(text: string, variables: { [key: string]: string }) {
		this.text = text;
		this.variables = variables;
	}
}

class QuestionGenerator {
	readonly format: string;
	readonly variableMap: { [key: string]: string[] };

	// Expects the following formats. 
	// Example #1
	// 		format: "Who of these is {job}?"
	// 		variableMap: {
	// 			"job": ["an engineer, "an astronaut", "a social worker"]
	// 		}
	//
	// Example #2
	// 		format: "Who of these is {job} and has a {vehicle}?"
	// 		variableMap: {
	// 			"job": ["an engineer, "an astronaut", "a social worker"],
	// 			"vehicle": ["motorbike", "car", "bycicle"]
	// 		}
	//
	constructor(format: string, variableMap: { [key: string]: string[] }) {
		this.format = format;
		this.variableMap = variableMap;
	}

	generateQuestion(): GeneratedQuestion {
		// Regular expression to match any {variable} pattern
		const VAR_EXPR = /\{([^}]+)\}/g;

		// Match the inside content of all results
		// For example, "{variable}" would collect just "variable"
		const variableKeys: Array<string> = Array<string>();
		let match: RegExpExecArray | null;
		while (match = VAR_EXPR.exec(this.format)) {
			if (match.length >= 1)
				variableKeys.push(match[1])
			else
				console.error("The regular expresion did not match at least two results.");
		}

		let generatedQuestion = this.format;
		let usedVariables: { [key: string]: string } = {};
		variableKeys.forEach((variableKey) => {
			if (this.variableMap[variableKey]) {
				// Choose a random value from the map with the variableKey matched
				const randomValue = this.variableMap[variableKey][Math.floor(Math.random() * this.variableMap[variableKey].length)];

				// Then, replace it in the question
				generatedQuestion = generatedQuestion.replace(`{${variableKey}}`, `<b>${randomValue}</b>`);
				usedVariables[variableKey] = randomValue;
			} else {
				console.error(`The variable map does not contain the key \"${variableKey}\"`)
			}
		})

		return new GeneratedQuestion(generatedQuestion, usedVariables);
	}
}
