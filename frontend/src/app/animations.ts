import { animate, AnimationEntryMetadata, state, style, transition, trigger } from '@angular/core';

// Component transition animations
export const slideInLeftAnimation: AnimationEntryMetadata =
  trigger('routeAnimation', [
    state('*',
      style({
        opacity: 1,
        transform: 'translateX(0)'
      })
    ),
    transition(':enter', [
      style({
        transform: 'translateX(100%)'
      }),
      animate('0.3s ease-in')
    ]),
    transition(':leave', [
      animate('0.3s ease-out', style({
        transform: 'translateX(100%)'
      }))
    ])
  ]);

export const slideInRightAnimation: AnimationEntryMetadata =
  trigger('routeAnimation', [
    state('*',
      style({
        opacity: 1,
        transform: 'translateX(0)'
      })
    ),
    transition(':enter', [
      style({
        transform: 'translateX(-100%)'
      }),
      animate('0.3s ease-in')
    ]),
    transition(':leave', [
      animate('0.3s ease-out', style({
        transform: 'translateX(-100%)'
      }))
    ])
  ]);
