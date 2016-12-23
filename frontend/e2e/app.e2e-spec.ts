import { MineservePage } from './app.po';

describe('mineserve App', function() {
  let page: MineservePage;

  beforeEach(() => {
    page = new MineservePage();
  });

  it('should display message saying app works', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('app works!');
  });
});
