function Header() {
  return (
    <header className="header">
      <div className="container header-content">
        <div className="header-logo">RunningHub</div>
        <nav className="header-nav">
          <a href="#" className="header-nav-link">文档</a>
          <a href="#" className="header-nav-link">示例</a>
          <a href="https://www.runninghub.cn" className="header-nav-link" target="_blank" rel="noopener noreferrer">
            官网
          </a>
        </nav>
      </div>
    </header>
  );
}

export default Header;
