#include <iostream>

class Node {
public:
    Node(int* value); // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-2-2-3]
    int* get() const;
private:
    int* value_;
};

Node::Node(int* value) : value_(value) {}
int* Node::get() const { return value_; }

int main() {
    Node node = nullptr;
    if (node.get() == nullptr) {
        std::cout << "null";
    }
    return 0;
}
