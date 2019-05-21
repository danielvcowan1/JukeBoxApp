import { Component } from '@angular/core';
import { ViewChild, ElementRef } from '@angular/core';

/**
 * Root component
 */
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
	title = 'Jukebox';

	constructor(private elementRef: ElementRef){}
 	ngAfterViewInit(){
    	this.elementRef.nativeElement.ownerDocument.body.style.backgroundColor = '#4C6085';
    }
}
