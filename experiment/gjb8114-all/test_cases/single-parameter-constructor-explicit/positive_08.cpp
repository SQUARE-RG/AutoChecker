#include <iostream>

class Node {
public:
    explicit Node(int* value);
    int* get() const;
private:
    int* value_;
};

Node::Node(int* value) : value_(value) {}
int* Node::get() const { return value_; }

int main() {
    Node node(nullptr);
    if (node.get() == nullptr) {
        std::cout << "null";
    }
    return 0;
}
