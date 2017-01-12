import { Injectable } from '@angular/core';
import { Step } from "./step";
import { BehaviorSubject} from "rxjs";

@Injectable()
export class StepsService {

  steps: Step[] = [
    new Step("1", "Choose game", true),
    new Step("2", "Settings"),
    new Step("3", "Payment"),
    new Step("4", "Confirmation")
  ];

  private _steps: BehaviorSubject<Step[]>;
  constructor() {
    this._steps = <BehaviorSubject<Step[]>>new BehaviorSubject([]);
    this.load();
  }
  getSteps() {
    return this._steps.asObservable();
  }
  load(){
    this._steps.next(this.steps);
  }
  increaseStep(stepIndex: number){
    console.log("increasing steps");
    console.log(stepIndex);

    for(let step of this.steps){
      console.log(step.highlighted);
      step.highlighted = false;
    }
    console.log(this.steps);
    this.steps[stepIndex].highlighted = true;
    this._steps.next(this.steps);
  }
}
