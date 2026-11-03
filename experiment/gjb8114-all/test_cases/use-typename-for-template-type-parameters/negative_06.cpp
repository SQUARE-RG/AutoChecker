template<typename T>
struct Box {
  static constexpr int kind = 0;
};

template<class T> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-1]
struct Box<T*> {
  static constexpr int kind = 1;
};

int main() {
  return Box<int*>::kind;
}
