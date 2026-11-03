#include <vector>
#include <iterator>

struct Item { int value; };

int main() {
    std::vector<Item> items = {{1}, {2}};
    auto it = std::next(items.begin());
    return it->value;
}
