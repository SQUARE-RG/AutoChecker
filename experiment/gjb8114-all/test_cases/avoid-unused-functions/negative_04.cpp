class Worker {
public:
    int public_value() const { return 1; }
private:
    int unused_helper() const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-3]
        return 2;
    }
};

int main() {
    Worker worker;
    return worker.public_value();
}
