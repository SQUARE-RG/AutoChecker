class SmallConstructor {
public:
    SmallConstructor() : counter(0) {
        counter += 1;
        counter += 1;
        counter += 1;
    }

    int get() const {
        return counter;
    }

private:
    int counter;
};

int main() {
    SmallConstructor instance;
    return instance.get();
}
