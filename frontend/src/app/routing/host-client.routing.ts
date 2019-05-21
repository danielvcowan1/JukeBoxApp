import { HostLayoutComponent } from '../components/host-layout/host-layout.component';
import { Routes, RouterModule } from '@angular/router';
import { ModuleWithProviders } from '@angular/core';

export const hostRoutes: Routes = [
    { path: '', component: HostLayoutComponent }
];

export const HostRouting: ModuleWithProviders = RouterModule.forChild(hostRoutes);