struct Node;

#include <ciso646>

struct Node {
    int value;
};

int main() {
    Node n{5};
    return n.value;
}
