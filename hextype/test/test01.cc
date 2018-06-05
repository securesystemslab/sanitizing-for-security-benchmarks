// Illegal based to derived casting of a heap allocated object
#include <iostream>

class Base {
public:
  Base() {}
  virtual void print() {
    std::cout << "Base" << std::endl;
  }
};

class Derived : public Base {
private:
  int extra;
public:
  Derived() : Base() {}
  virtual void print() {
    std::cout << "Derived" << std::endl;
  }
};

__attribute__((noinline))
Derived *illegal_cast(Base *b) {
  return static_cast<Derived *>(b);
}

int main() {
  Base *b = new Base();
  b->print();

  Derived *d = illegal_cast(b);
  d->print();

  delete b;
}
