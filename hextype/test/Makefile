all: test01.hextype

%.o: %.cc
	$(CXX) $(CXXFLAGS) -o $@ -c $<

%.hextype : %.o
	$(CXX) $(LDFLAGS) -o $@ $<

.PHONY: test clean

test:
	./test01.hextype

clean:
	 $(RM) *.hextype *.o
