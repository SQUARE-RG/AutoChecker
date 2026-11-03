class Worker {
public:
    int public_value() const { return helper(); }
private:
    int helper() const { return 2; }
};

int main() {
    Worker worker;
    return worker.public_value();
}
