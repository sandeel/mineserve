export class Step{
  stepNumber: string;
  stepText: string;
  highlighted: Boolean;

  constructor(stepNumber: string, stepText: string, highlighted: Boolean=false){
    this.stepNumber = stepNumber;
    this.stepText = stepText;
    this.highlighted = highlighted;
  }
}
