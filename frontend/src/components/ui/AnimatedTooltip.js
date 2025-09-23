import React from "react";

const AnimatedTooltip = ({ items }) => {
  return (
    <div className="flex flex-row items-center justify-center mb-10 w-full">
      <div className="flex flex-row items-center space-x-4">
        {items.map((person, idx) => (
          <div
            key={person.id}
            className="relative group cursor-pointer"
            style={{
              transform: `translateX(${idx * -20}px)`,
            }}
          >
            <div className="w-16 h-16 rounded-full border-2 border-white overflow-hidden transition-all duration-300 group-hover:scale-110">
              <img
                src={person.image}
                alt={person.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 bg-black text-white px-3 py-2 rounded-lg text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <div className="font-semibold">{person.name}</div>
              <div className="text-xs text-gray-300">{person.designation}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export { AnimatedTooltip };
