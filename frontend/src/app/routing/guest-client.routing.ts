import { Routes, RouterModule } from '@angular/router';
import { ModuleWithProviders } from '@angular/core';
import { GuestLayoutComponent } from '../components/guest-layout/guest-layout.component';

export const guestRoutes: Routes = [
    { path: '', component: GuestLayoutComponent }
];

export const GuestRouting: ModuleWithProviders = RouterModule.forChild(guestRoutes);