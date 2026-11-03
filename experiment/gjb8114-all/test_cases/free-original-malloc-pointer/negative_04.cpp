#include <cstdlib>

struct Pair {
    int first;
    int second;
};

int main() {
    Pair *pair = static_cast<Pair*>(std::malloc(sizeof(Pair)));
    if (pair == nullptr) {
        return 1;
    }

    pair->first = 1;
    pair->second = 2;

    int *member = &pair->second;
    *member = 3;

    std::free(member); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-17]
    return 0;
}
