.. _techniques-rigs-solving-maya-rigs-ref:

Solving Maya Rigs
=================

MM Solver can be used to solve the controls of a Maya rig, for example
a deforming biped or quadruped character, or rigid object, such as a
vehicle or prop.

To get started, you will need:

- 3D Geometry representing a real-world object.

- A Maya Rig with Controls to deform or transform the 3D geometry.

For very simple rigs, such as a rigid object, a rig may not be needed.

Rigid Transformations
+++++++++++++++++++++

Rigid transformations are the easiest and fastest to solve with MM
Solver. Rigid transformations use the translation, rotation and scale
XYZ values to move 3D geometry.

If your target object is moving with rigid motion, always solve rigid
transformations because these will provide the best quality, with the
least number of 2D Markers and 3D Bundles. Even if an object is not
perfectly rigid, solving rigidly may provide a good starting point to
manually tweak or solve deformations.

For an in-depth example of rigid solving (with a hierarchy) the
:ref:`Robot Arm - Rigid Hierarchy Solving
<tutorial-robot-arm-rigid-hierarchy-solving>` tutorial will
provide details.

To solve a rigid object:

#. Create 2D Markers for your object.

#. Parent the 3D Bundles of your Markers under the object's
   transform node.

#. Move the 3D Bundles to the correct 3D position on the object, and
   lock the translation XYZ attributes.

#. Open the :ref:`Solver UI <solver-ui-ref>`.

#. Select and add the 2D Markers to the *Input Objects* section of the
   *Solver UI* (with the *+* button).

#. Select your object's transform node, in the Channel Box, select the
   attributes that you wish to solve.

#. Add the selected attributes to the *Output Attributes* section
   (with the *+* button).

#. Press *Solve* button in the *Solver UI*.

Rigid Solving Tips
------------------

- Limit the number of attributes, needed for solving; lock all
  attributes that cannot move.

  - e.g. If a vehicle is moving along the flat ground, place the car
    on the ground and lock the translation Y attribute.

  - e.g. A door can only rotate from the pivot point of the hinges,
    create a transform node at the hinges, and parent your object
    under the transform node, then solve for the rotation of the door
    hinge - probably only a single attribute.

- Avoid solving scale because the solver can quickly get confused.

  - If you must solve an object's scale, try to limit to a single
    attribute (X, Y or Z).

  - If you need to solve the uniform scale of an object you must
    create connections from *Scale Y* to *Scale X* and *Scale Z*.
    This will allow you to solve only *Scale Y*, but both *Scale X*
    and *Scale Z* will have the exact same value. You can create these
    connections using Maya's *Connection Editor* window.

- Avoid large attribute values. MM Solver can get confused when an
  attribute is very large. Try to avoid using very large values for
  transformations (for example 10,000 units away from origin).

- When talking about rigid transforms, it's easy to refer to
  translation attributes as TXYZ rather than "Translation X, Y and
  Z". Same goes for Rotation ("RXYZ"), and Scale ("SXYZ").

Solving Rig Controls
++++++++++++++++++++

Maya Rigs will contain *Controls* that are used to move the rig in
specific ways. For example Rig Controls may perform the following:

- Inverse Kinematics (IK) - e.g. a control for a hand or foot.

- Forward Kinematics (FK) - just regular rigid transformations in a
  hierarchy.

- Control Space Switching - controls moving *with* different parts of
  a character; head, hips, chest, etc.

- Special attributes controlling blend shapes, hand poses, doors
  opening, or anything else.

MM Solver is (technically) able to solve any floating-point of
attribute in the Maya scene. As a result any of the IK, FK or
"Special" attributes can be solved with MM Solver, but there is a
trick (see note below).

It is **highly recommended** to avoid solving rig controls directly,
if possible, because of the solver performance. As soon as a Rig
control is added (even indirectly) into MM Solver, MM Solver *must*
switch to a slower mode to evaluate Maya nodes. If only transforms,
cameras, markers and bundles are used, MM Solver can use a highly
optimized mode to speed up the solver performance. Transform
hierarchies and direct Maya DG connections are also supported by this
special mode.

The fastest way to solve rig controls is to not solve rig controls
directly, and instead use controller transforms, such as *locators*
nodes, or use the :ref:`create-remove-controller-tool-ref` tool.

For example, lets solve the head of a biped character:

#. Select the character's head, and body controls, and use the
   :ref:`create-remove-controller-tool-ref` tool to create locators
   parent constrained back to the character's body and head.

   This will allow our head to move using the controller locator,
   rather than the rig control.

#. Parent the body controller under the head controller.

#. Create 2D Markers for the character's head.

#. Parent the 3D Bundles of your Markers under the head controller
   node.

#. Move (snap) the 3D Bundles to the correct 3D position on the head,
   and lock the translation XYZ attributes.

   If you align your character's head to the plate, you can use the
   :ref:`project-marker-on-mesh-tool-ref` tool to position the bundles
   easily on the surface of the mesh.

#. Open the :ref:`Solver UI <solver-ui-ref>`.

#. Select and add the 2D Markers to the *Input Objects* section of the
   *Solver UI* (with the *+* button).

#. Select the head controller node, in the Channel Box, select the
   attributes that you wish to solve.

#. Add the selected attributes to the *Output Attributes* section
   (with the *+* button).

#. Press *Solve* button in the *Solver UI*.

This approach treats the character rig as a rigid transformation, and
avoids using the character rig directly in the solver. Sometimes this
is not possible, and you must evaluate and solve the Maya Rig's 3D
geometry in the solver, to do this you can :ref:`Solve Rivets
<techniques-rigs-solving-rivets-ref>`.

.. note:: In Maya 2020+ you may experience **incorrect solves** when
          solving Maya rig controls directly. If you do experience MM
          Solver evaluating/solving incorrectly, the workaround is to
          enable the :ref:`solver-ui-evaluate-mesh-rivets-ref`
          check-box in the *Solver UI*. This will slow down the solver
          performance but will ensure correct evaluation of the Maya
          nodes. This is a known issue and is trying to be improved.

.. _techniques-rigs-solving-rivets-ref:

Solving Rivets
++++++++++++++

Sometimes it is very important to solve a Maya rig deforming, for a
"skin-tight" MatchMove. Common examples are for deformations of faces,
jaws, arms or chest of a character.

When solving deformations, we must evaluate the Maya rig geometry at
specific positions on the surface. For example, we could track a 2D
Marker for a character's eye lid. We must then find the 3D surface
position and "rivet" the 3D Bundle to the surface, so that it locks
and moves along the surface of the character's geometry.

Unfortunately, solving rivets can be **very slow** in MM Solver, so it
is always recommended to use rigid solving approaches first, before
solving Rivets.

MM Solver does not contain Riveting tools (yet), however the "classic"
`rivet.mel`_ script has been tested with MM Solver and is known to
work. Other riveting scripts and tools (such as the new Maya 2020
Rivet tool) may work, but are untested.

To make sure that MM Solver can evaluate the Maya Rivet nodes, it is
critical to **enable** the :ref:`solver-ui-evaluate-mesh-rivets-ref`
check-box in the Solver UI before solving.

Therefore the rough steps for solving rivets are:

#. Track 2D Markers for deforming surfaces (such as human skin).

#. Unlock the Maya Rig's geometry to make it selectable (this is
   dependent on the rig).

#. Create Rivets for the 3D positions on the character's geometry.

   - After `rivet.mel`_ script is installed, select 2 adjacent Mesh
     edges and type "rivet" in the Maya MEL Command Line, then press
     enter; a new locator node named "rivet1" will be created.

#. Parent your 3D Bundle under the "rivet" locator, position the
   Bundle and lock the translation XYZ attributes.

   If you align your character's head to the plate, you can use the
   :ref:`project-marker-on-mesh-tool-ref` tool to position the bundles
   easily on the surface of the mesh.

#. Open the :ref:`Solver UI <solver-ui-ref>`.

#. Select and add the 2D Markers to the *Input Objects* section of the
   *Solver UI* (with the *+* button).

#. Select your object's transform node, in the Channel Box, select the
   attributes (such as the character's head and jaw control) that you
   wish to solve.

#. Add the selected attributes to the *Output Attributes* section
   (with the *+* button).

#. It is **important** to enable
   :ref:`solver-ui-evaluate-mesh-rivets-ref` in the *Solver UI* to
   correctly evaluate and solve the rivet positions.

#. Press *Solve* button in the *Solver UI*.

.. note:: MM Solver is *not* a facial animation tool, and has not been
  designed for that purpose.

.. _rivet.mel:
   https://www.highend3d.com/maya/script/rivet-button-for-maya
