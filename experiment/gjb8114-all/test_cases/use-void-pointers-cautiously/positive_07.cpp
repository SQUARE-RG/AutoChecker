#include <cstddef>
#include <iostream>
#include <string>
#include <vector>

template <typename T>
class TypedStorage {
public:
    void add(T* item) {
        items_.push_back(item);
    }

    T* get(std::size_t index) const {
        return items_.at(index);
    }

    std::size_t size() const {
        return items_.size();
    }

private:
    std::vector<T*> items_;
};

int main() {
    int intValue = 42;
    std::string stringValue = "hello";

    TypedStorage<int> intStorage;
    TypedStorage<std::string> stringStorage;

    intStorage.add(&intValue);
    stringStorage.add(&stringValue);

    std::cout << *intStorage.get(0) << " " << *stringStorage.get(0) << std::endl;
    return 0;
}
