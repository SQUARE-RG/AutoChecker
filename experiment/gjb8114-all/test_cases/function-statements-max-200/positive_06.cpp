class SmallDestructor {
public:
    SmallDestructor() : counter(0) {}

    ~SmallDestructor() {
        counter += 1;
        counter += 1;
        counter += 1;
    }

private:
    int counter;
};

int main() {
    SmallDestructor instance;
    return 0;
}
