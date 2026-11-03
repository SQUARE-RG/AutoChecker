#include <iostream>

class Temperature {
public:
    Temperature();
    void SetCelsius(int value);
    int GetCelsius() const;

private:
    int celsius_;
};

Temperature::Temperature() : celsius_(0) {}

void Temperature::SetCelsius(int value) {
    celsius_ = value;
}

int Temperature::GetCelsius() const {
    return celsius_;
}

int main() {
    Temperature temperature;
    temperature.SetCelsius(21);
    std::cout << temperature.GetCelsius() << '\n';
    return 0;
}
