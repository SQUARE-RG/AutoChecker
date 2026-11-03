#include <cstring>

class MixedOwner {
public:
    MixedOwner() : count(new int(0)), name(new char[32]) {
        name[0] = '\0';
    }

    MixedOwner(const MixedOwner& other)
        : count(new int(*other.count)), name(new char[32]) {
        std::strncpy(name, other.name, 32);
        name[31] = '\0';
    }

    MixedOwner& operator=(const MixedOwner& other) {
        if (this != &other) {
            int* newCount = new int(*other.count);
            char* newName = new char[32];
            std::strncpy(newName, other.name, 32);
            newName[31] = '\0';

            delete count;
            delete[] name;
            count = newCount;
            name = newName;
        }
        return *this;
    }

    ~MixedOwner() {
        delete count;
        delete[] name;
    }

    void setCount(int value) { *count = value; }

private:
    int* count;
    char* name;
};

int main() {
    MixedOwner first;
    first.setCount(9);
    MixedOwner second(first);
    MixedOwner third;
    third = second;
    return 0;
}
