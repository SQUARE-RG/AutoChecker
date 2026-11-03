#include <iostream>

struct Node {
    int value;
    Node* next;
};

int main() {
    Node third{3, nullptr};
    Node second{2, &third};
    Node first{1, &second};

    int sum = 0;
    Node* current = &first;
    while (current != nullptr) {
        sum += current->value;
        current = current->next;
    }
    std::cout << sum << '\n';
    return 0;
}
