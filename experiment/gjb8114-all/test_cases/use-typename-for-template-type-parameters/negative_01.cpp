template <class T>  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-1]
struct Box {
    T value;
};

int main() {
    Box<int> box{42};
    return box.value;
}
