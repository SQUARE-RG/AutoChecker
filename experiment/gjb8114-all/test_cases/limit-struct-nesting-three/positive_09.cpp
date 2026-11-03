struct Outer {
  struct Middle {
    void run() {
      auto f = [] {
        struct L1 {};
      };
      f();
    }
  };
};

int main() {
  Outer::Middle m;
  m.run();
  return 0;
}
