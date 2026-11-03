#include <cstring>

class MixedOwner { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-1]
public:
    MixedOwner() : count(new int(0)), name(new char[32]) {
        name[0] = '\0';
    }

    MixedOwner(const MixedOwner& other)
        : count(new int(*other.count)), name(new char[32]) {
        std::strncpy(name, other.name, 32);
        name[31] = '\0';
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
    MixedOwner owner;
    owner.setCount(7);
    return 0;
}
