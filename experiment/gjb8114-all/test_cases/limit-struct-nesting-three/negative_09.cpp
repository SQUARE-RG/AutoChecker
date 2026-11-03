struct Outer {
  struct Middle {
    void run() {
      auto f = [] {
        struct L1 {
          struct L2 {}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-5]
        };
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
