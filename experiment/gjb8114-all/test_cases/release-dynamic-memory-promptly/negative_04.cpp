// Negative: constructor allocates memory but the class has no destructor to release it.

class Holder {
public:
    Holder() : data(new int(7)) {} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-3]
    int get() const { return *data; }

private:
    int* data;
};

int main() {
    Holder holder;
    return holder.get();
}
