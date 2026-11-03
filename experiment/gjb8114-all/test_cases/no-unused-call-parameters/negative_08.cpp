class Box {
public:
    Box& operator=(const Box& other) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-2]
        return *this;
    }

    int value = 0;
};

int main() {
    Box a;
    Box b;
    a = b;
    return a.value;
}
