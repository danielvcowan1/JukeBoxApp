import { Component } from '@angular/core';
import { ApiService } from 'src/app/services/api.service';

/**
 * Start page
 */
@Component({
  selector: 'start-page',
  templateUrl: './start.component.html',
  styleUrls: ['./start.component.css']
})
export class StartComponent {

  data: string;

  constructor(private apiService: ApiService) { }

  private getDataFromApi() {
    this.apiService.getData().subscribe(data => {
      this.data = JSON.stringify(data);
    });
  }

}