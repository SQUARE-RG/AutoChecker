template<typename T>
struct Box {
  static constexpr int kind = 0;
};

template<typename T>
struct Box<T*> {
  static constexpr int kind = 1;
};

int main() {
  return Box<int*>::kind;
}
